from llobot.environments.replay import ReplayEnv

def test_replay_env_default():
    """Tests the default state of ReplayEnv."""
    env = ReplayEnv()
    assert not env.recording()
    assert env.replaying()

def test_replay_env_recording():
    """Tests enabling recording."""
    env = ReplayEnv()
    env.start_recording()
    assert env.recording()
    assert not env.replaying()
