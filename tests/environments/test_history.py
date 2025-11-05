from __future__ import annotations
from datetime import datetime
from pathlib import Path
from llobot.environments import Environment
from llobot.environments.history import SessionHistory
from llobot.environments.persistent import PersistentEnv
from llobot.environments.session import SessionEnv
from llobot.utils.time import format_time

class DummyPersistent(PersistentEnv):
    """
    A simple persistent component used to verify that SessionHistory
    saves and loads environment state to the path derived from SessionEnv.
    """
    filename = 'dummy.txt'
    loaded_value: str | None

    def __init__(self):
        self.loaded_value = None

    def save(self, directory: Path):
        (directory / self.filename).write_text('saved', encoding='utf-8')

    def load(self, directory: Path):
        path = directory / self.filename
        if path.exists():
            self.loaded_value = path.read_text(encoding='utf-8')
        else:
            self.loaded_value = None

def test_save_uses_session_id_and_persists_component(tmp_path: Path):
    env = Environment()
    # Register persistent component so Environment.save() has something to write.
    env[DummyPersistent]
    # Set session ID.
    session_id = datetime(2025, 5, 6, 7, 46, 8)
    env[SessionEnv].set_id(session_id)

    history = SessionHistory(tmp_path)

    # Execute save.
    history.save(env)

    # Verify file written at path derived from the session ID.
    session_dir = tmp_path / format_time(session_id)
    assert (session_dir / DummyPersistent.filename).exists()

def test_load_uses_session_id_and_loads_component(tmp_path: Path):
    # Prepare saved state.
    session_id = datetime(2025, 5, 6, 7, 46, 8)
    session_dir = tmp_path / format_time(session_id)
    session_dir.mkdir(parents=True, exist_ok=True)
    (session_dir / DummyPersistent.filename).write_text('saved', encoding='utf-8')

    # Create fresh environment and set same session ID.
    env = Environment()
    env[SessionEnv].set_id(session_id)
    # Ensure the component exists so Environment.load() can load it immediately.
    dp = env[DummyPersistent]

    history = SessionHistory(tmp_path)
    history.load(env)

    assert dp.loaded_value == 'saved'
