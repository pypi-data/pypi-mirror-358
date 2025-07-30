# Pearl RL

A reinforcement learning library with explainability features for AI/ML research and development.

## Features

- **Reinforcement Learning Agents**: Implementation of various RL algorithms including DQN
- **Environment Wrappers**: Easy integration with Gymnasium environments
- **Explainability Methods**: Multiple explainability techniques including LIME, SHAP, and LMUT
- **Stability Analysis**: Tools for analyzing model stability
- **Pre-built Environments**: Support for Atari games and Lunar Lander

## Installation

```bash
pip install pearl-rl
```

## Quick Start

```python
from pearl import Pearl
from pearl.agents import SimpleDQN
from pearl.enviroments import GymRLEnv

# Create an environment
env = GymRLEnv("LunarLander-v2")

# Create an agent
agent = SimpleDQN(env.observation_space, env.action_space)

# Create Pearl instance
pearl = Pearl(agent, env)

# Train the agent
pearl.train(episodes=1000)

# Get explanations
explanations = pearl.explain(episode=0)
```

## Documentation

For detailed documentation and examples, please visit our [documentation page](https://github.com/yourusername/pearl).

## Contributing

We welcome contributions! Please see our [contributing guidelines](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use Pearl in your research, please cite:

```bibtex
@software{pearl_rl,
  title={Pearl RL: A Reinforcement Learning Library with Explainability Features},
  author={Your Name},
  year={2024},
  url={https://github.com/yourusername/pearl}
}
``` 