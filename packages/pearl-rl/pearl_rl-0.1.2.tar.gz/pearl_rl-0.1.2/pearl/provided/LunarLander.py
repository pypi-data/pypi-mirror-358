import numpy as np
from pearl.mask import Mask

class LunarLanderTabularMask(Mask):
    """
    Dynamic heuristic mask for LunarLander with 8D state.
    Weights each feature by importance and current state value to emphasize relevant actions.
    Features: [x_pos, y_pos, x_vel, y_vel, angle, angular_vel, leg1_contact, leg2_contact]
    Actions: [Do nothing, Fire left, Fire main, Fire right]
    """
    # approximate max abs values for normalization
    _feature_scales = np.array([1.5, 1.5, 2.0, 2.0, np.pi, 5.0, 1.0, 1.0], dtype=np.float32)

    def __init__(self, action_space: int):
        super().__init__(action_space)
        self.action_space = action_space
        self.weights = self._define_weights()
        self.last_obs = None

    def _define_weights(self) -> np.ndarray:
        # Base static weights shape: (features, actions)
        w = np.zeros((8, self.action_space), dtype=np.float32)
        # Do nothing: prefer stable (low velocity & angle)
        w[:, 0] = np.array([0.2, 0.1, 0.5, 0.5, 0.7, 0.5, 0.3, 0.3])
        # Fire left (rotate right): act when x_vel < 0 or angle < 0
        w[:, 1] = np.array([0.4, 0.0, 0.7, 0.0, 1.0, 0.7, 0.1, 0.1])
        # Fire main: when falling fast (y_vel negative) and far from pad (y_pos high)
        w[:, 2] = np.array([0.0, 0.8, 0.0, 1.2, 0.5, 0.0, 0.0, 0.0])
        # Fire right (rotate left): act when x_vel > 0 or angle > 0
        w[:, 3] = np.array([0.4, 0.0, 0.7, 0.0, 1.0, 0.7, 0.1, 0.1])
        return w

    def update(self, obs: np.ndarray):
        # obs shape: (1,8)
        self.last_obs = obs.reshape(-1)

    def compute(self, attr: np.ndarray) -> np.ndarray:
        # attr: (1, features, 1, 1, actions)
        _, C, _, _, A = attr.shape
        if self.last_obs is None:
            # fallback to static weighting if no state
            return np.sum(self.weights * np.sum(attr, axis=(0,2,3)), axis=0)

        # normalize obs
        scaled = np.abs(self.last_obs) / self._feature_scales
        # clip to [0,1]
        scaled = np.clip(scaled, 0.0, 1.0)

        scores = np.zeros(A, dtype=np.float32)
        # dynamic weight = static weight * scaled state magnitude
        for a in range(A):
            for c in range(C):
                feature_attr_sum = np.sum(attr[0, c, :, :, a])
                dyn_w = self.weights[c, a] * (1.0 + scaled[c])  # amplify weight by state
                scores[a] += dyn_w * feature_attr_sum
        return scores
