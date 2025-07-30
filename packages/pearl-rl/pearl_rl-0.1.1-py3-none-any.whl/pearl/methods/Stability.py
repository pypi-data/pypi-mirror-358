from typing import Any
import os
import numpy as np
import torch
import matplotlib.pyplot as plt

from pearl.agent import RLAgent
from pearl.env import RLEnvironment
from pearl.method import ExplainabilityMethod

idd = 0  # global image counter for visualization


def add_salt_and_pepper_noise(tensor: torch.Tensor, amount: float = 0.01) -> torch.Tensor:
  """
  Add salt and pepper noise to a tensor image. Assumes image is in [0, 1] range.

  Parameters:
    tensor: (B, C, H, W) or (C, H, W)
    amount: fraction of pixels to alter
  """
  noisy = tensor.clone()

  # Determine if batch dimension exists
  has_batch = tensor.dim() == 4

  # Calculate total pixels and number to modify
  total_elements = tensor.numel()
  elements_per_item = total_elements // tensor.shape[0] if has_batch else total_elements
  num_pixels = int(amount * elements_per_item)

  # Create random indices in one go instead of looping
  if has_batch:
    batch_size = tensor.shape[0]
    # Generate random indices for each batch item
    for b in range(batch_size):
      # Generate all random indices at once
      indices = torch.randperm(elements_per_item)[:num_pixels]
      # Convert to multi-dimensional indices
      c, h, w = np.unravel_index(indices.cpu().numpy(), tensor.shape[1:])

      # Set values to either 0 or 1 randomly
      values = torch.randint(0, 2, (num_pixels,), dtype=torch.float32, device=tensor.device)
      noisy[b, c, h, w] = values
  else:
    # Generate all random indices at once
    indices = torch.randperm(elements_per_item)[:num_pixels]
    # Convert to multi-dimensional indices
    c, h, w = np.unravel_index(indices.cpu().numpy(), tensor.shape)

    # Set values to either 0 or 1 randomly
    values = torch.randint(0, 2, (num_pixels,), dtype=torch.float32, device=tensor.device)
    noisy[c, h, w] = values

  return noisy


def show_obs_and_noisy(obs: np.ndarray, noisy_obs: np.ndarray, title: str = "", save_path: str = "./temp/"):
    """
    Visualize stacked grayscale frames before and after noise.
    Assumes obs and noisy_obs are (C, H, W), typically (4, 84, 84)
    """
    global idd
    os.makedirs(save_path, exist_ok=True)
    save_file = os.path.join(save_path, f"obs_{idd}.png")
    idd += 1

    num_frames = obs.shape[0]
    fig, axs = plt.subplots(2, num_frames, figsize=(2 * num_frames, 4))

    for i in range(num_frames):
        axs[0, i].imshow(obs[i], cmap='gray', vmin=0, vmax=255)
        axs[0, i].set_title(f"Original {i+1}")
        axs[0, i].axis('off')

        axs[1, i].imshow(noisy_obs[i], cmap='gray', vmin=0, vmax=255)
        axs[1, i].set_title(f"Noisy {i+1}")
        axs[1, i].axis('off')

    plt.suptitle(title)
    plt.tight_layout()
    plt.savefig(save_file)
    plt.close(fig)


class StabilityExplainability(ExplainabilityMethod):
    def __init__(self, device, noise_type: str = 'salt_pepper', noise_std: float = 0.01, num_samples: int = 20):
        """
        noise_type: 'gaussian' or 'salt_pepper'
        """
        super().__init__()
        self.device = device
        self.noise_std = noise_std
        self.num_samples = num_samples
        self.noise_type = noise_type
        self.agents = None
        self.env = None

    def set(self, env: RLEnvironment):
        super().set(env)
        self.env = env

    def prepare(self, agents: list[RLAgent]):
        print(f"Preparing StabilityExplainability with {len(agents)} agents.")
        self.agents = agents

    def onStep(self, action: Any):
        pass

    def onStepAfter(self, action: Any):
        pass

    def _apply_noise(self, tensor: torch.Tensor) -> torch.Tensor:
        if self.noise_type == 'gaussian':
            noise = torch.normal(mean=0.0, std=self.noise_std, size=tensor.shape).to(self.device)
            return (tensor + noise).clamp(0.0, 1.0)
        elif self.noise_type == 'salt_pepper':
            return add_salt_and_pepper_noise(tensor, amount=self.noise_std)
        else:
            raise ValueError(f"Unsupported noise type: {self.noise_type}")

    def explain(self, obs) -> np.ndarray | Any:
        """
        Return an array with shape (num_agents,) representing the number of consistent actions
        under noise for each agent.
        """
        global idd
        obs_tensor = torch.as_tensor(obs, dtype=torch.float, device=self.device)



        with torch.no_grad():
            noisy_tensor = self._apply_noise(obs_tensor)
            obs_np = (obs_tensor.squeeze(0).cpu().numpy() * 255).astype(np.uint8)
            noisy_np = (noisy_tensor.squeeze(0).cpu().numpy() * 255).astype(np.uint8)

            if idd == 0:
                show_obs_and_noisy(obs_np, noisy_np, title="Original vs Noisy")

        result = []
        for agent in self.agents:
            base_action = agent.predict(obs_tensor)
            consistent = 0

            for _ in range(self.num_samples):
                noisy_obs = self._apply_noise(obs_tensor)
                noisy_action = agent.predict(noisy_obs)
                if noisy_action == base_action:
                    consistent += 1

            result.append(consistent)

        return np.array(result)

    def value(self, obs, reward: dict = None) -> list[float]:
        stability_scores = self.explain(obs)
        if reward is not None:
            weighted_scores = []
            for i, score in enumerate(stability_scores):
                agent_reward = reward.get(i, 1.0)  # Default to 1.0 if no reward provided
                weighted_scores.append(score * agent_reward)
            return weighted_scores
        return stability_scores.tolist()
