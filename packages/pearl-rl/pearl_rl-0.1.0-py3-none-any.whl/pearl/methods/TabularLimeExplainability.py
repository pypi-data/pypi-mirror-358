from typing import List, Any
import numpy as np
import torch
from lime.lime_tabular import LimeTabularExplainer
from pearl.agent import RLAgent
from pearl.env import RLEnvironment
from pearl.mask import Mask
from pearl.method import ExplainabilityMethod


class TabularLimeExplainability(ExplainabilityMethod):
    def __init__(self, device: torch.device, mask: Mask, feature_names: List[str], training_data: np.ndarray):
        """
        :param device: torch device
        :param mask: Mask object for score computation
        :param feature_names: Names of each feature in the state vector
        :param training_data: A sample of the environment's state space to train the explainer
        """
        super().__init__()
        self.device = device
        self.mask = mask
        self.feature_names = feature_names
        self.training_data = training_data
        self.explainer = LimeTabularExplainer(
            training_data,
            feature_names=feature_names,
            class_names=[str(i) for i in range(mask.action_space)],
            mode="classification",
            discretize_continuous=True
        )
        self.agents: List[RLAgent] = []

    def set(self, env: RLEnvironment):
        super().set(env)

    def prepare(self, agents: List[RLAgent]):
        self.agents = agents

    def onStep(self, action: Any): pass
    def onStepAfter(self, action: Any): pass

    def explain(self, obs: np.ndarray) -> List[Any]:
        if not self.agents:
            raise ValueError("Call prepare() before explain().")

        obs_vec = obs.squeeze()  # (C,) or (1, C)
        if obs_vec.ndim == 2:
            obs_vec = obs_vec[0]

        explanations = []
        for agent in self.agents:
            model = agent.get_q_net().to(self.device).eval()

            def predict_fn(x: np.ndarray) -> np.ndarray:
                with torch.no_grad():
                    x_tensor = torch.tensor(x, dtype=torch.float32).to(self.device)
                    logits = model(x_tensor)
                    # Logits don't add up to 1, so we use softmax
                    probs = torch.softmax(logits, dim=1).cpu().numpy()
                return probs


            exp = self.explainer.explain_instance(
                data_row=obs_vec,
                predict_fn=predict_fn,
                num_features=len(self.feature_names),
                top_labels=self.mask.action_space
            )
            explanations.append(exp)
        return explanations

    def value(self, obs: np.ndarray) -> List[float]:
        exps = self.explain(obs)
        self.mask.update(obs)
        values: List[float] = []

        obs_tensor = torch.tensor(obs, dtype=torch.float32, device=self.device)
        for i, exp in enumerate(exps):
            q = self.agents[i].get_q_net()
            if q is None:
                q_vals = self.agents[i].policy_net(obs_tensor).detach()
            else:
                q_vals = q(obs_tensor).detach()

            action = int(torch.argmax(q_vals))

            # Create feature importance vector for each action
            weights = np.zeros(obs.shape[-1])
            for fid, weight in exp.local_exp[action]:
                weights[fid] = weight

            # Fix shape for broadcasting
            attribution = np.abs(weights).reshape(1, obs.shape[-1], 1, 1, 1)
            attribution = np.broadcast_to(attribution, (1, obs.shape[-1], 1, 1, self.mask.action_space)).astype(np.float32)

            score = float(self.mask.compute(attribution)[action])
            action_q = q_vals[0, action].item()
            max_q = torch.max(q_vals).item()
            confidence = action_q / max_q if max_q != 0 else 1.0

            values.append(score * confidence)
        return values
