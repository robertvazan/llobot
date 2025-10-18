import pytest
from pathlib import Path
from llobot.environments import Environment
from llobot.environments.persistent import PersistentEnv

class MyComponent:
    def __init__(self):
        self.value = 123

class AnotherComponent:
    pass

class DummyPersistentComponent(PersistentEnv):
    def __init__(self):
        self.data = ''

    def save(self, directory: Path):
        (directory / 'dummy.txt').write_text(self.data)

    def load(self, directory: Path):
        path = directory / 'dummy.txt'
        if path.exists():
            self.data = path.read_text()

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

def test_environment_persistence(tmp_path: Path):
    """Tests saving and loading an environment."""
    env1 = Environment()
    p = env1[DummyPersistentComponent]
    p.data = "hello"
    env1[MyComponent] # non-persistent component

    save_path = tmp_path / "env"
    env1.save(save_path)

    assert (save_path / 'dummy.txt').read_text() == "hello"

    # Test loading into a new environment
    env2 = Environment()
    env2.load(save_path)
    p2 = env2[DummyPersistentComponent]
    assert p2.data == "hello"

def test_environment_lazy_load(tmp_path: Path):
    """Tests lazy loading of persistent components."""
    env1 = Environment()
    p = env1[DummyPersistentComponent]
    p.data = "lazy"
    save_path = tmp_path / "env"
    env1.save(save_path)

    env2 = Environment()
    env2.load(save_path) # p2 is not created yet
    # check that it's not loaded
    assert DummyPersistentComponent not in env2._components
    p2 = env2[DummyPersistentComponent]
    assert p2.data == "lazy"

def test_environment_load_existing(tmp_path: Path):
    """Tests loading for already existing components."""
    env1 = Environment()
    p = env1[DummyPersistentComponent]
    p.data = "existing"
    save_path = tmp_path / "env"
    env1.save(save_path)

    env2 = Environment()
    p2 = env2[DummyPersistentComponent]
    assert p2.data == '' # default value
    env2.load(save_path)
    assert p2.data == "existing"

def test_save_empty_environment_does_not_create_dir(tmp_path: Path):
    env = Environment()
    env[MyComponent]
    save_path = tmp_path / "env"
    env.save(save_path)
    assert not save_path.exists()
