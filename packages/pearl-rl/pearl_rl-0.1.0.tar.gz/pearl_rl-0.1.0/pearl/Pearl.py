"""
Main Pearl class for reinforcement learning with explainability.
"""

from typing import Any, Dict, List, Optional
from .agent import Agent
from .env import Environment
from .method import Method


class Pearl:
    """
    Main Pearl class that combines agents, environments, and explainability methods.
    """
    
    def __init__(self, agent: Agent, environment: Environment):
        """
        Initialize Pearl with an agent and environment.
        
        Args:
            agent: The reinforcement learning agent
            environment: The environment to train in
        """
        self.agent = agent
        self.environment = environment
        self.training_history = []
        self.explanation_methods = {}
        
    def train(self, episodes: int = 1000, **kwargs) -> List[Dict[str, Any]]:
        """
        Train the agent in the environment.
        
        Args:
            episodes: Number of episodes to train for
            **kwargs: Additional training parameters
            
        Returns:
            List of training metrics for each episode
        """
        print(f"Training for {episodes} episodes...")
        
        for episode in range(episodes):
            state = self.environment.reset()
            done = False
            total_reward = 0
            steps = 0
            
            while not done:
                action = self.agent.act(state)
                next_state, reward, done, info = self.environment.step(action)
                
                # Store experience for learning
                self.agent.store_experience(state, action, reward, next_state, done)
                
                # Learn from experience
                if self.agent.should_learn():
                    self.agent.learn()
                
                state = next_state
                total_reward += reward
                steps += 1
            
            # Record episode metrics
            episode_metrics = {
                'episode': episode,
                'total_reward': total_reward,
                'steps': steps,
                'epsilon': getattr(self.agent, 'epsilon', None)
            }
            self.training_history.append(episode_metrics)
            
            if episode % 100 == 0:
                print(f"Episode {episode}: Reward = {total_reward}, Steps = {steps}")
        
        print("Training completed!")
        return self.training_history
    
    def explain(self, episode: int = 0, method: str = "lime") -> Dict[str, Any]:
        """
        Generate explanations for a specific episode.
        
        Args:
            episode: Episode number to explain
            method: Explanation method to use
            
        Returns:
            Dictionary containing explanation results
        """
        if episode >= len(self.training_history):
            raise ValueError(f"Episode {episode} not found in training history")
        
        print(f"Generating {method} explanation for episode {episode}...")
        
        # This is a placeholder - implement actual explanation logic
        explanation = {
            'episode': episode,
            'method': method,
            'explanation': f"Explanation for episode {episode} using {method}",
            'confidence': 0.85
        }
        
        return explanation
    
    def evaluate(self, episodes: int = 100) -> Dict[str, float]:
        """
        Evaluate the trained agent.
        
        Args:
            episodes: Number of episodes to evaluate
            
        Returns:
            Dictionary containing evaluation metrics
        """
        print(f"Evaluating agent over {episodes} episodes...")
        
        total_rewards = []
        total_steps = []
        
        for episode in range(episodes):
            state = self.environment.reset()
            done = False
            episode_reward = 0
            episode_steps = 0
            
            while not done:
                action = self.agent.act(state, training=False)
                next_state, reward, done, info = self.environment.step(action)
                
                state = next_state
                episode_reward += reward
                episode_steps += 1
            
            total_rewards.append(episode_reward)
            total_steps.append(episode_steps)
        
        evaluation_metrics = {
            'mean_reward': sum(total_rewards) / len(total_rewards),
            'std_reward': (sum((r - sum(total_rewards) / len(total_rewards)) ** 2 for r in total_rewards) / len(total_rewards)) ** 0.5,
            'mean_steps': sum(total_steps) / len(total_steps),
            'episodes': episodes
        }
        
        print(f"Evaluation completed: Mean reward = {evaluation_metrics['mean_reward']:.2f}")
        return evaluation_metrics
    
    def save_model(self, filepath: str):
        """
        Save the trained agent model.
        
        Args:
            filepath: Path to save the model
        """
        self.agent.save(filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """
        Load a trained agent model.
        
        Args:
            filepath: Path to the model file
        """
        self.agent.load(filepath)
        print(f"Model loaded from {filepath}")
    
    def get_training_history(self) -> List[Dict[str, Any]]:
        """
        Get the training history.
        
        Returns:
            List of training metrics for each episode
        """
        return self.training_history
