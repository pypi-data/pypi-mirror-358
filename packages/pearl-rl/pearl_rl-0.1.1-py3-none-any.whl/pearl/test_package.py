#!/usr/bin/env python3
"""
Test script to verify Pearl package functionality.
"""

def test_imports():
    """Test that all main modules can be imported."""
    try:
        import pearl
        print("✓ Successfully imported pearl")
        
        from pearl import Pearl
        print("✓ Successfully imported Pearl class")
        
        from pearl.agent import Agent
        print("✓ Successfully imported Agent class")
        
        from pearl.env import Environment
        print("✓ Successfully imported Environment class")
        
        from pearl.method import Method
        print("✓ Successfully imported Method class")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_version():
    """Test that version information is available."""
    try:
        import pearl
        print(f"✓ Pearl version: {pearl.__version__}")
        return True
    except AttributeError:
        print("✗ Version information not available")
        return False

def test_basic_functionality():
    """Test basic Pearl functionality."""
    try:
        from pearl import Pearl
        from pearl.agent import Agent
        from pearl.env import Environment
        
        # Create mock agent and environment classes for testing
        class MockAgent(Agent):
            def act(self, state, training=True):
                return 0
            
            def store_experience(self, state, action, reward, next_state, done):
                pass
            
            def should_learn(self):
                return False
            
            def learn(self):
                pass
            
            def save(self, filepath):
                pass
            
            def load(self, filepath):
                pass
        
        class MockEnvironment(Environment):
            def reset(self):
                return [0, 0, 0, 0]
            
            def step(self, action):
                return [0, 0, 0, 0], 0, True, {}
        
        # Create Pearl instance
        agent = MockAgent()
        env = MockEnvironment()
        pearl = Pearl(agent, env)
        
        print("✓ Successfully created Pearl instance")
        
        # Test training (just one episode)
        history = pearl.train(episodes=1)
        print(f"✓ Training completed: {len(history)} episodes")
        
        # Test evaluation
        metrics = pearl.evaluate(episodes=1)
        print(f"✓ Evaluation completed: mean reward = {metrics['mean_reward']}")
        
        return True
    except Exception as e:
        print(f"✗ Functionality test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Pearl Package Test")
    print("=" * 30)
    
    tests = [
        ("Import Test", test_imports),
        ("Version Test", test_version),
        ("Functionality Test", test_basic_functionality),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nRunning {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print(f"\n{'='*30}")
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Package is ready for distribution.")
    else:
        print("⚠️  Some tests failed. Please fix issues before publishing.")
    
    return passed == total

if __name__ == "__main__":
    main() 