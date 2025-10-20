import tempfile
from pathlib import Path
import pytest
from llobot.environments import Environment
from llobot.environments.model import ModelEnv
from llobot.models.echo import EchoModel
from llobot.models.library.named import NamedModelLibrary

default_model = EchoModel('default')
m1 = EchoModel('m1')
m2 = EchoModel('m2')
library = NamedModelLibrary(m1, m2)

def test_get_default():
    env = Environment()
    model_env = env[ModelEnv]
    model_env.configure(library, default_model)
    assert model_env.get() == default_model

def test_select_and_get():
    env = Environment()
    model_env = env[ModelEnv]
    model_env.configure(library, default_model)
    assert model_env.select('m1') == m1
    assert model_env.get() == m1
    assert model_env.select('m3') is None
    assert model_env.get() == m1

def test_get_no_default_or_selection():
    env = Environment()
    model_env = env[ModelEnv]
    model_env.configure(library, None)
    with pytest.raises(ValueError, match="No model selected and no default model configured."):
        model_env.get()

def test_save_and_load():
    with tempfile.TemporaryDirectory() as tempdir_str:
        tempdir = Path(tempdir_str)

        # Save
        env_save = Environment()
        model_env_save = env_save[ModelEnv]
        model_env_save.configure(library, default_model)
        model_env_save.select('m2')
        env_save.save(tempdir)
        assert (tempdir / 'model.txt').read_text() == 'm2\n'

        # Load
        env_load = Environment()
        model_env_load = env_load[ModelEnv]
        model_env_load.configure(library, default_model)
        env_load.load(tempdir)
        assert model_env_load.get() == m2

def test_load_nonexistent_key():
    with tempfile.TemporaryDirectory() as tempdir_str:
        tempdir = Path(tempdir_str)
        (tempdir / 'model.txt').write_text('nonexistent\n')

        env = Environment()
        model_env = env[ModelEnv]
        model_env.configure(library, default_model)
        with pytest.raises(ValueError, match="Model key 'nonexistent' from model.txt not found in library."):
            env.load(tempdir)

def test_save_no_selection():
    with tempfile.TemporaryDirectory() as tempdir_str:
        tempdir = Path(tempdir_str)
        env = Environment()
        model_env = env[ModelEnv]
        model_env.configure(library, default_model)
        env.save(tempdir)
        assert not (tempdir / 'model.txt').exists()
