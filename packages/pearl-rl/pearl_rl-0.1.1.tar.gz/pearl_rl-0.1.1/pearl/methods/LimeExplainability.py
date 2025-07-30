from typing import Any, List
import numpy as np
import torch
from lime import lime_image
from skimage.color import gray2rgb
from skimage.transform import resize
from pearl.agent import RLAgent
from pearl.env import RLEnvironment
from pearl.mask import Mask
from pearl.method import ExplainabilityMethod
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import os

class LimeExplainability(ExplainabilityMethod):
    """
    LIME explainability aligned with mask.compute input format (1,C,H,W,A).
    Adds confidence-weighted scoring.
    """
    def __init__(self, device: torch.device, mask: Mask):
        super().__init__()
        self.device = device
        self.mask = mask
        self.agents: List[RLAgent] = []
        self.explainer = lime_image.LimeImageExplainer()
        
        # Tracking for visualizations
        self.step_count = 0
        self.max_steps_to_visualize = 10
        self.heatmaps_dir = "lime_heatmaps"
        
        # Create directory for heatmaps if it doesn't exist
        if not os.path.exists(self.heatmaps_dir):
            os.makedirs(self.heatmaps_dir)

    def set(self, env: RLEnvironment):
        super().set(env)

    def prepare(self, agents: List[RLAgent]):
        self.agents = agents

    def onStep(self, action: Any): pass
    def onStepAfter(self, action: Any): pass

    def explain(self, obs: np.ndarray) -> List:
        if not self.agents:
            raise ValueError("Call prepare() before explain().")

        frame = obs.squeeze()  # (C, H, W)
        img = np.transpose(frame, (1,2,0))
        if img.shape[2] != 3:
            img = img[:,:,:3] if img.shape[2] > 3 else gray2rgb(img[:,:,0])

        explanations = []
        n_actions = self.mask.action_space
        for agent in self.agents:
            model = agent.get_q_net().to(self.device).eval()
            def batch_predict(images: np.ndarray) -> np.ndarray:
                gr = np.mean(images, axis=3, keepdims=True).astype(np.float32)/255.0
                stacked = np.repeat(gr, frame.shape[0], axis=3)
                tensor = torch.tensor(np.transpose(stacked, (0,3,1,2)), dtype=torch.float32).to(self.device)
                with torch.no_grad(): out = model(tensor)
                return out.cpu().numpy()
          
            exp = self.explainer.explain_instance(
                image=img.astype(np.double),
                classifier_fn=batch_predict,
                top_labels=n_actions,
                hide_color=0,
                num_samples=100,
                
            )
            explanations.append(exp)
            
            # Create visualization if we're within the first max_steps_to_visualize steps
            if self.step_count <= self.max_steps_to_visualize:
                self._visualize_heatmap(img, exp, agent_idx=len(explanations)-1)
        return explanations

    def value(self, obs: np.ndarray) -> List[float]:
        exps = self.explain(obs)
        self.mask.update(obs)
        values: List[float] = []
        C,H,W = obs.shape[1:]
        A = self.mask.action_space

        for i, exp in enumerate(exps):
            # Predict action and get Q-values
            obs_t = torch.as_tensor(obs, dtype=torch.float32, device=self.device)
            with torch.no_grad():
                q = self.agents[i].get_q_net()(obs_t)
            action = int(torch.argmax(q))

            # Build per-action importance maps
            segs = exp.segments
            maps = np.zeros((A, H, W), dtype=float)
            for lbl, pairs in exp.local_exp.items():
                for seg_id, wt in pairs:
                    maps[lbl, segs==seg_id] = wt
            if segs.shape != (H,W):
                maps = np.stack([resize(m, (H,W), preserve_range=True, anti_aliasing=True) for m in maps], axis=0)

            # Construct attribution tensor (1,C,H,W,A)
            maps_hw_a = np.transpose(maps, (1,2,0))
            attributions = np.broadcast_to(maps_hw_a[None,None,:,:,:], (1, C, H, W, A)).astype(np.float32)
            
            # get the absolute value of the attributions
            attributions = np.abs(attributions)
            # Normalize the attributions
            # attributions = attributions / np.sum(attributions, axis=(1,2,3), keepdims=True)

            # Base mask score
            score = float(self.mask.compute(attributions)[action])
            # Confidence: action Q over max Q
            action_q = q[0, action].item()
            max_q = torch.max(q).item()
            confidence = action_q / max_q if max_q != 0 else 1.0

            values.append(score * confidence)
        return values


    def _visualize_heatmap(self, img: np.ndarray, explanation, agent_idx: int = 0):
        """Generate and save a heatmap visualization for the current step."""
        # Convert visualization image back to 4-channel format expected by model
        # Original observation is (C,H,W) where C=4
        obs_4ch = np.mean(img, axis=2, keepdims=True)  # Convert to grayscale (H,W,1)
        obs_4ch = np.repeat(obs_4ch, 4, axis=2)        # Repeat to 4 channels (H,W,4)
        obs_4ch = np.transpose(obs_4ch, (2,0,1))       # To (4,H,W)
        obs_t = torch.as_tensor(obs_4ch[None], dtype=torch.float32, device=self.device)
        
        with torch.no_grad():
            q = self.agents[agent_idx].get_q_net()(obs_t)
        action = int(torch.argmax(q))
        
        # Get the explanation for the predicted action
        temp, mask = explanation.get_image_and_mask(
            label=action, 
            positive_only=False, 
            hide_rest=False, 
            num_features=10
        )
        
        # Create figure with two subplots
        plt.figure(figsize=(14, 6))
        
        # Plot original image (show just first 3 channels for visualization)
        plt.subplot(1, 2, 1)
        plt.imshow(img if img.shape[2] == 3 else img[:,:,:3])
        plt.title(f"Original Image - Step {self.step_count}")
        plt.axis('off')
        
        # Plot heatmap overlay
        plt.subplot(1, 2, 2)
        
        # Create a custom colormap: blue is negative, red is positive
        colors = [(0, 0, 1), (1, 1, 1), (1, 0, 0)]  # Blue -> White -> Red
        cmap = LinearSegmentedColormap.from_list('BrBG', colors, N=256)
        
        # Get the explanation segments
        segs = explanation.segments
        
        # Create a heatmap from the explanation
        heatmap = np.zeros(segs.shape, dtype=np.float32)
        for segment, importance in explanation.local_exp[action]:
            heatmap[segs == segment] = importance
            
        # Normalize heatmap for better visualization
        abs_max = np.max(np.abs(heatmap))
        if abs_max > 0:
            heatmap = heatmap / abs_max
        
        # Show heatmap with the right colormap
        plt.imshow(img if img.shape[2] == 3 else img[:,:,:3])
        plt.imshow(heatmap, cmap=cmap, alpha=0.7, vmin=-1, vmax=1)
        plt.colorbar(label='Feature Importance')
        action_names = ["NOOP", "FIRE", "UP", "RIGHT", "LEFT", "RIGHTFIRE", "LEFTFIRE"] # PLACEHOLDER: SHOULD BE IN ENV
        plt.title(f"LIME Attribution Heatmap - Action {action_names[action]}, Step {self.step_count}")
        plt.axis('off')
        
        # Save the figure
        filename = os.path.join(self.heatmaps_dir, f"heatmap_step_{self.step_count}_agent_{agent_idx}.png")
        plt.savefig(filename, bbox_inches='tight', dpi=150)
        plt.close()
        
        # Increment step count
        self.step_count += 1