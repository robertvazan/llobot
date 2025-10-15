from datetime import timedelta
import pytest
from llobot.utils.time import current_time
from llobot.environments.cutoff import CutoffEnv

def test_cutoff_env_get_default():
    env = CutoffEnv()
    assert env.get() is None

def test_cutoff_env_set_and_get():
    env = CutoffEnv()
    cutoff1 = current_time()
    env.set(cutoff1)
    assert env.get() == cutoff1

    # Setting same cutoff is ok
    env.set(cutoff1)
    assert env.get() == cutoff1

def test_cutoff_env_set_different_fails():
    env = CutoffEnv()
    cutoff1 = current_time()
    env.set(cutoff1)

    cutoff2 = cutoff1 + timedelta(seconds=1)
    with pytest.raises(ValueError):
        env.set(cutoff2)

    assert env.get() == cutoff1

def test_cutoff_env_clear():
    env = CutoffEnv()
    cutoff1 = current_time()
    env.set(cutoff1)
    assert env.get() is not None

    env.clear()
    assert env.get() is None

    # After clearing, a new cutoff can be set.
    cutoff2 = cutoff1 + timedelta(seconds=1)
    env.set(cutoff2)
    assert env.get() == cutoff2
