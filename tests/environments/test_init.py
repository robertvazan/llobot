import pytest
from llobot.environments import Environment, EnvBase

class MyComponent(EnvBase):
    def __init__(self):
        self.value = 123

class AnotherComponent(EnvBase):
    pass

class NotAComponent:
    pass

def test_environment():
    """Tests component management within the Environment."""
    env = Environment()

    # First access creates the component and sets up back-reference
    comp1 = env[MyComponent]
    assert isinstance(comp1, MyComponent)
    assert comp1.value == 123
    assert comp1.env is env

    # Second access returns the same instance
    comp2 = env[MyComponent]
    assert comp1 is comp2

    # Access another component
    another = env[AnotherComponent]
    assert isinstance(another, AnotherComponent)
    assert another.env is env

    # Check they are different components
    assert comp1 is not another

    # Test type safety: getting a non-EnvBase class should fail
    with pytest.raises(TypeError):
        env[NotAComponent]

def test_env_base():
    """Tests edge cases of the EnvBase.env property."""
    # Test unattached component
    comp = MyComponent()
    with pytest.raises(RuntimeError, match="Component is not attached to an environment."):
        _ = comp.env

    # Test destroyed environment
    env = Environment()
    comp_attached = env[MyComponent]
    assert comp_attached.env is env
    del env
    with pytest.raises(RuntimeError, match="Environment has been destroyed."):
        _ = comp_attached.env
