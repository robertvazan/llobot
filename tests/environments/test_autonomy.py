import tempfile
from pathlib import Path
import pytest
from llobot.environments import Environment
from llobot.environments.autonomy import AutonomyEnv
from llobot.roles.autonomy import NoAutonomy, HopAutonomy

default_autonomy = NoAutonomy()
hop_autonomy = HopAutonomy()
profiles = {'hop': hop_autonomy}

def test_get_default():
    env = Environment()
    autonomy_env = env[AutonomyEnv]
    autonomy_env.configure(default_autonomy, profiles)
    assert autonomy_env.get() == default_autonomy
    assert autonomy_env.selected_name is None

def test_select_and_get():
    env = Environment()
    autonomy_env = env[AutonomyEnv]
    autonomy_env.configure(default_autonomy, profiles)
    assert autonomy_env.select('hop') == hop_autonomy
    assert autonomy_env.get() == hop_autonomy
    assert autonomy_env.selected_name == 'hop'
    assert autonomy_env.select('unknown') is None
    assert autonomy_env.get() == hop_autonomy  # Selection persists if new selection fails
    assert autonomy_env.selected_name == 'hop'

def test_save_and_load():
    with tempfile.TemporaryDirectory() as tempdir_str:
        tempdir = Path(tempdir_str)

        # Save
        env_save = Environment()
        autonomy_env_save = env_save[AutonomyEnv]
        autonomy_env_save.configure(default_autonomy, profiles)
        autonomy_env_save.select('hop')
        env_save.save(tempdir)
        assert (tempdir / 'autonomy.txt').read_text() == 'hop\n'

        # Load
        env_load = Environment()
        autonomy_env_load = env_load[AutonomyEnv]
        autonomy_env_load.configure(default_autonomy, profiles)
        env_load.load(tempdir)
        assert autonomy_env_load.get() == hop_autonomy
        assert autonomy_env_load.selected_name == 'hop'

def test_load_unknown_profile():
    with tempfile.TemporaryDirectory() as tempdir_str:
        tempdir = Path(tempdir_str)
        (tempdir / 'autonomy.txt').write_text('unknown\n')

        env = Environment()
        autonomy_env = env[AutonomyEnv]
        autonomy_env.configure(default_autonomy, profiles)

        with pytest.raises(ValueError, match="Autonomy profile 'unknown' from autonomy.txt not found."):
            env.load(tempdir)

def test_save_no_selection():
    with tempfile.TemporaryDirectory() as tempdir_str:
        tempdir = Path(tempdir_str)
        env = Environment()
        autonomy_env = env[AutonomyEnv]
        autonomy_env.configure(default_autonomy, profiles)
        env.save(tempdir)
        assert not (tempdir / 'autonomy.txt').exists()
