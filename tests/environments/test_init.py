import pytest
from llobot.environments import Environment

class MyComponent:
    def __init__(self):
        self.value = 123

class AnotherComponent:
    pass

def test_environment():
    """Tests component management within the Environment."""
    env = Environment()

    # First access creates the component
    comp1 = env[MyComponent]
    assert isinstance(comp1, MyComponent)
    assert comp1.value == 123

    # Second access returns the same instance
    comp2 = env[MyComponent]
    assert comp1 is comp2

    # Access another component
    another = env[AnotherComponent]
    assert isinstance(another, AnotherComponent)

    # Check they are different components
    assert comp1 is not another
