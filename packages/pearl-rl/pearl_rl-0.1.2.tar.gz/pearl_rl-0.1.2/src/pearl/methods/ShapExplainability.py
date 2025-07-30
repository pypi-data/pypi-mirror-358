from typing import Any

import numpy as np
import shap
import torch

from pearl.agent import RLAgent
from pearl.env import RLEnvironment
from pearl.mask import Mask
from pearl.method import ExplainabilityMethod

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import os

# A little hack to fix the issue of shap not being able to handle Flatten layer
from shap.explainers._deep import deep_pytorch
deep_pytorch.op_handler['Flatten'] = deep_pytorch.passthrough

class ShapExplainability(ExplainabilityMethod):
    def __init__(self, device, mask: Mask):
        super().__init__()
        self.device = device
        self.explainer = None
        self.background = None
        self.mask = mask
        self.agents = None
        
         # Visualization parameters
        self.step_count = 0
        self.max_steps_to_visualize = 10
        self.heatmaps_dir = "shap_heatmaps"
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.heatmaps_dir):
            os.makedirs(self.heatmaps_dir)

    def set(self, env: RLEnvironment):
        super().set(env)
        self.background = torch.zeros(env.get_observations().shape).to(self.device)

    def prepare(self, agents: list[RLAgent]):
        self.explainer = []
        self.agents = agents
        for agent in agents:
            model = agent.get_q_net().to(self.device)
            self.explainer.append(shap.DeepExplainer(model, self.background))

    def onStep(self, action: Any):
        # nothing for shap
        pass

    def onStepAfter(self, action: Any):
        # nothing for shap
        pass

    def explain(self, obs) -> np.ndarray | Any:
        if self.explainer is None:
            raise ValueError("Explainer not set. Please call prepare() first.")

        obs_tensor = torch.as_tensor(obs, dtype=torch.float, device=self.device)
        result = []
        for i, explainer in enumerate(self.explainer):
            shap_values = explainer.shap_values(obs_tensor, check_additivity=False) # Fixme: check_additivity should be true .. but I set it to false for now
            result.append(shap_values) 
        
            # Create visualization if we're within the first max_steps_to_visualize steps
            if self.step_count <= self.max_steps_to_visualize:
                self._visualize_heatmap(obs, shap_values, agent_idx=i)
        return result

    def value(self, obs) -> list[float]:
        explains = self.explain(obs)
        values = []
        obs_tensor = torch.as_tensor(obs, dtype=torch.float, device=self.device)
        for i, explain in enumerate(explains):
            agent = self.agents[i]
            self.mask.update(obs)
            scores = self.mask.compute(explain)
            action = agent.predict(obs_tensor)
            values.append(scores[action])
        return values
    
    def _visualize_heatmap(self, obs: np.ndarray, shap_values: list, agent_idx: int = 0):
        """Generate and save a SHAP heatmap visualization for the current step."""
        try:
            # Get the predicted action
            obs_tensor = torch.as_tensor(obs, dtype=torch.float, device=self.device)
            with torch.no_grad():
                q_values = self.agents[agent_idx].get_q_net()(obs_tensor)
            action = int(torch.argmax(q_values))
            
            # Prepare the image for visualization
            img = obs.squeeze()  # Remove batch dimension if present
            if img.ndim == 3 and img.shape[0] == 4:  # (C,H,W)
                img = np.transpose(img[:3], (1, 2, 0))  # Convert to (H,W,3)
                img = (img - img.min()) / (img.max() - img.min())  # Normalize
            elif img.ndim == 2:  # (H,W)
                img = np.stack([img]*3, axis=-1)  # Convert to RGB
            
            # Handle different SHAP values structures
            if isinstance(shap_values, list):
                # If we get a list, take the first element (assuming it's the one we want)
                shap_values = shap_values[0]
                
            # Now handle the 5D shape (1, 4, 84, 84, 7)
            if shap_values.ndim == 5:
                # Select the action we're explaining
                action_shap = shap_values[0, :, :, :, action]  # Shape (4, 84, 84)
            elif shap_values.ndim == 4:
                action_shap = shap_values[0]  # Take first sample
            elif shap_values.ndim == 3:
                action_shap = shap_values
            else:
                print(f"Unexpected SHAP values shape: {shap_values.shape}")
                return
            
            # Rest of your visualization code remains the same...
            # Create figure with two subplots
            plt.figure(figsize=(14, 6))
            
            # Plot original image
            plt.subplot(1, 2, 1)
            plt.imshow(img)
            plt.title(f"Original Image - Step {self.step_count}")
            plt.axis('off')
            
            # Plot SHAP heatmap overlay
            plt.subplot(1, 2, 2)
            
            # Create a custom colormap
            colors = [(0, 0, 1), (1, 1, 1), (1, 0, 0)]  # Blue -> White -> Red
            cmap = LinearSegmentedColormap.from_list('BrBG', colors, N=256)
            
            # Sum across channels for visualization
            heatmap = np.sum(action_shap, axis=0) if action_shap.ndim == 3 else action_shap
            
            # Normalize heatmap
            abs_max = np.max(np.abs(heatmap))
            if abs_max > 0:
                heatmap = heatmap / abs_max
            
            # Show heatmap
            plt.imshow(img)
            plt.imshow(heatmap, cmap=cmap, alpha=0.7, vmin=-1, vmax=1)
            plt.colorbar(label='SHAP Value')
            action_names = ["NOOP", "FIRE", "UP", "RIGHT", "LEFT", "RIGHTFIRE", "LEFTFIRE"] # PLACEHOLDER: SHOULD BE IN ENV
            plt.title(f"SHAP Attribution - Action {action_names[action]}, Step {self.step_count}")
            plt.axis('off')
            
            # Save the figure
            filename = os.path.join(self.heatmaps_dir, f"shap_heatmap_step_{self.step_count}_agent_{agent_idx}.png")
            plt.savefig(filename, bbox_inches='tight', dpi=150)
            plt.close()
            
            self.step_count += 1
        
        except Exception as e:
            print(f"Error generating SHAP heatmap: {e}")
            print(f"SHAP values type: {type(shap_values)}")
            if hasattr(shap_values, 'shape'):
                print(f"SHAP values shape: {shap_values.shape}")
            print(f"Action: {action}")