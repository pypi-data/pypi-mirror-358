"""
Pearl RL - A reinforcement learning model selection library using explainability.
"""

__version__ = "0.1.1"
__author__ = "Youssef Rabie & Abdelrahman Mohamed Mahmoud Sobhy & Youssef Hagag"
__email__ = "yousef.mohamed.rabia@gmail.com"

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