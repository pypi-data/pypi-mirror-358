"""
Pearl RL - A reinforcement learning library with explainability features.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .Pearl import Pearl
from .agent import RLAgent as Agent
from .env import Environment
from .method import Method

__all__ = [
    "Pearl",
    "Agent", 
    "Environment",
    "Method",
] 