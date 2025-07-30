from typing import Any

import numpy as np
import torch
import matplotlib.pyplot as plt
from sklearn.tree import plot_tree
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression
from sklearn.utils.validation import check_is_fitted

from pearl.agent import RLAgent
from pearl.env import RLEnvironment
from pearl.mask import Mask
from pearl.method import ExplainabilityMethod


class LinearModelUTreeExplainability(ExplainabilityMethod):
    def __init__(self, device, mask: Mask):
        super().__init__()
        self.device = device
        self.explainer = None
        self.mask = mask
        self.agents = None
        self.trees = None
        self.linear_models = None
        self.training_data = []
        self.training_targets = []
        self.original_shape = None

    def set(self, env: RLEnvironment):
        super().set(env)
        obs = env.get_observations()
        self.original_shape = obs.shape  # Store original shape for later reshaping
        self.input_dim = np.prod(obs.shape[1:])  # Total number of features

    def prepare(self, agents: list[RLAgent]):
        self.agents = agents
        self.trees = []
        self.linear_models = []
        
        for _ in agents:
            # Initialize a decision tree for feature selection
            tree = DecisionTreeRegressor(max_depth=5, min_samples_leaf=5)
            # Initialize a linear model for each leaf node
            linear_model = LinearRegression()
            self.trees.append(tree)
            self.linear_models.append(linear_model)

    def onStep(self, action: Any):
        # nothing for LMUT
        pass

    def onStepAfter(self, action: Any):
        # nothing for LMUT
        pass

    def add_training_data(self, obs, q_values):
        """Add training data for fitting the models"""
        self.training_data.append(obs)
        self.training_targets.append(q_values)

    def fit_models(self):
        """Fit the decision trees and linear models with collected data"""
        if not self.training_data or not self.training_targets:
            raise ValueError("No training data available. Call add_training_data first.")

        # Convert training data to 2D array
        X = np.vstack(self.training_data)  # Stack all observations into a 2D array
        y = np.vstack(self.training_targets)  # Stack all targets into a 2D array

        for i, (tree, linear_model) in enumerate(zip(self.trees, self.linear_models)):
            # Fit the decision tree
            tree.fit(X, y[:, i])
            
            # Get the leaf nodes for each sample
            leaf_indices = tree.apply(X)
            
            # Fit linear models for each leaf node
            unique_leaves = np.unique(leaf_indices)
            for leaf in unique_leaves:
                mask = leaf_indices == leaf
                if np.sum(mask) > 1:  # Only fit if we have enough samples
                    linear_model.fit(X[mask], y[mask, i])

    def explain(self, obs) -> np.ndarray | Any:
        if self.trees is None or self.linear_models is None:
            raise ValueError("Explainer not set. Please call prepare() first.")

        try:
            # Check if models are fitted using scikit-learn's validation
            for tree in self.trees:
                check_is_fitted(tree)
        except Exception as e:
            raise ValueError("Models not fitted. Call fit_models() first.") from e

        obs_tensor = torch.as_tensor(obs, dtype=torch.float, device=self.device)
        result = []
        
        for i, (tree, linear_model) in enumerate(zip(self.trees, self.linear_models)):
            # Get feature importance from the tree
            tree_importance = tree.feature_importances_
            # Get linear model coefficients
            linear_importance = linear_model.coef_ if hasattr(linear_model, 'coef_') else np.zeros(self.input_dim)
            # Combine both importances
            combined_importance = (tree_importance + linear_importance) / 2
            
            # Get the number of actions from the environment
            n_actions = self.env.action_space.n
            
            # Detect environment type based on observation shape
            obs_shape = self.original_shape
            
            if len(obs_shape) == 4:  # Image-based environment (e.g., Space Invaders)
                # Shape: (batch, channels, height, width)
                # Reshape to original image shape
                reshaped_importance = combined_importance.reshape(obs_shape)
                # Expand to include action channels
                expanded_importance = np.expand_dims(reshaped_importance, axis=-1)
                expanded_importance = np.repeat(expanded_importance, n_actions, axis=-1)
                
            elif len(obs_shape) == 2:  # Tabular environment (e.g., Lunar Lander)
                # Shape: (batch, features)
                # Remove batch dimension and create 5D tensor for mask compatibility
                reshaped_importance = combined_importance.reshape(obs_shape[1:])  # Remove batch dimension
                # Create the expected 5D tensor shape: (1, features, 1, 1, actions)
                expanded_importance = np.expand_dims(reshaped_importance, axis=0)  # Add batch dim
                expanded_importance = np.expand_dims(expanded_importance, axis=2)  # Add height dim
                expanded_importance = np.expand_dims(expanded_importance, axis=3)  # Add width dim
                expanded_importance = np.expand_dims(expanded_importance, axis=4)  # Add action dim
                expanded_importance = np.repeat(expanded_importance, n_actions, axis=4)  # Repeat for all actions
                
            else:
                # Handle other cases (1D, 3D, etc.)
                # Try to reshape to original shape and add action dimension
                try:
                    reshaped_importance = combined_importance.reshape(obs_shape)
                    expanded_importance = np.expand_dims(reshaped_importance, axis=-1)
                    expanded_importance = np.repeat(expanded_importance, n_actions, axis=-1)
                except:
                    # Fallback: create a simple 5D tensor
                    reshaped_importance = combined_importance.reshape(-1)
                    expanded_importance = np.zeros((1, len(reshaped_importance), 1, 1, n_actions))
                    for a in range(n_actions):
                        expanded_importance[0, :, 0, 0, a] = reshaped_importance
            
            result.append(expanded_importance)
            
        return result

    def value(self, obs) -> list[float]:
        explains = self.explain(obs)
        values = []
        
        for i, explain in enumerate(explains):
            agent = self.agents[i]
            # Reshape observation back to original shape for the mask
            obs_original = obs.reshape(self.original_shape)
            self.mask.update(obs_original)
            scores = self.mask.compute(explain)
            # Convert to tensor and use original shape for DQN prediction
            obs_tensor = torch.as_tensor(obs_original, dtype=torch.float, device=self.device)
            action = agent.predict(obs_tensor)
            values.append(scores[action])
            
        return values

    def visualize_tree_structure(self, agent_idx=0, save_path=None, show_plot=True, feature_names=None):
        """
        Visualize the decision tree structure.
        
        Args:
            agent_idx: Index of the agent to visualize (default: 0)
            save_path: Path to save the visualization (optional)
            show_plot: Whether to display the plot (default: True)
            feature_names: List of feature names to display instead of x[i] (optional)
        """
        if self.trees is None:
            raise ValueError("Explainer not set. Please call prepare() first.")

        try:
            check_is_fitted(self.trees[agent_idx])
        except Exception as e:
            raise ValueError("Models not fitted. Call fit_models() first.") from e

        tree = self.trees[agent_idx]
        
        # Auto-generate feature names if not provided
        if feature_names is None:
            obs_shape = self.original_shape
            if len(obs_shape) == 4:  # Image-based environment
                # Shape: (batch, channels, height, width)
                channels, height, width = obs_shape[1], obs_shape[2], obs_shape[3]
                feature_names = []
                
                # Create meaningful names for image pixels
                for c in range(channels):
                    for h in range(height):
                        for w in range(width):
                            # Use channel and position information
                            feature_names.append(f"ch{c}_pos_{h}x{w}")
                                
            elif len(obs_shape) == 2:  # Tabular environment
                # Shape: (batch, features)
                num_features = obs_shape[1]
                feature_names = [f"feature_{i}" for i in range(num_features)]
            else:
                # Generic naming for other cases
                num_features = np.prod(obs_shape[1:])
                feature_names = [f"feature_{i}" for i in range(num_features)]
        
        # Create tree visualization with much wider figure and better spacing
        fig, ax = plt.subplots(1, 1, figsize=(35, 20))  # Even wider and taller
        
        # Use sklearn's tree plotting with parameters to prevent collapsing
        plot_tree(tree, ax=ax, filled=True, rounded=True, fontsize=10, 
                 feature_names=feature_names, class_names=None, precision=3,
                 proportion=True, max_depth=None)
        ax.set_title(f'Decision Tree Structure for Agent {agent_idx}', fontsize=18, pad=25)
        
        # Adjust layout to prevent node overlapping
        plt.tight_layout(pad=2.0)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        if show_plot:
            plt.show()
        else:
            plt.close()
        
        return fig

    def collect_training_data(self, num_samples: int = 1000):
        """Collect training data by running the environment and gathering Q-values from agents.
        
        Args:
            num_samples (int): Number of training samples to collect. Defaults to 1000.
        """
        from tqdm import tqdm
        
        for _ in tqdm(range(num_samples), desc="Collecting training samples"):
            obs = self.env.get_observations()
            obs_tensor = torch.as_tensor(obs, dtype=torch.float, device=self.device)
            
            # Get Q-values from all agents
            q_values = []
            for agent in self.agents:
                with torch.no_grad():
                    q_vals = agent.get_q_net()(obs_tensor).cpu().numpy()
                    # Take the maximum Q-value for each agent
                    q_values.append(np.max(q_vals, axis=1))
            q_values = np.array(q_values).T  # Shape: (batch_size, n_agents)
            
            # Reshape observation to 2D array (flatten all dimensions except batch)
            obs_reshaped = obs.reshape(obs.shape[0], -1)  # This will give us (batch_size, features)
            self.add_training_data(obs_reshaped, q_values)
            
            # Take a random action to get new observations
            action = self.env.action_space.sample()
            state, reward_dict, terminated, truncated, info = self.env.step(action)
            if terminated:
                self.env.reset()