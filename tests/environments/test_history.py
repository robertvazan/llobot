from __future__ import annotations
import base64
import hashlib
from pathlib import Path
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.thread import ChatThread
from llobot.environments import Environment
from llobot.environments.history import SessionHistory
from llobot.environments.persistent import PersistentEnv
from llobot.environments.prompt import PromptEnv

class DummyPersistent(PersistentEnv):
    """
    A simple persistent component used to verify that SessionHistory
    saves and loads environment state to the path derived from PromptEnv.
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

def _session_hash(text: str) -> str:
    hasher = hashlib.sha256(text.encode('utf-8'))
    b64 = base64.urlsafe_b64encode(hasher.digest()).decode('ascii')
    return b64[:40]

def test_save_uses_session_id_and_persists_component(tmp_path: Path):
    env = Environment()
    # Register persistent component so Environment.save() has something to write.
    env[DummyPersistent]
    # Set prompt to derive session ID.
    prompt_env = env[PromptEnv]
    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "initial prompt")])
    prompt_env.set(prompt)
    session_id = prompt_env.hash
    assert session_id

    history = SessionHistory(tmp_path)

    # Execute save.
    history.save(env)

    # Verify file written at path derived from the session ID.
    session_dir = tmp_path / session_id
    assert (session_dir / DummyPersistent.filename).exists()

def test_load_uses_session_id_and_loads_component(tmp_path: Path):
    # Prepare saved state using computed session ID for "initial prompt".
    session_id = _session_hash("initial prompt")
    session_dir = tmp_path / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    (session_dir / DummyPersistent.filename).write_text('saved', encoding='utf-8')

    # Create fresh environment and set same prompt.
    env = Environment()
    prompt_env = env[PromptEnv]
    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "initial prompt")])
    prompt_env.set(prompt)
    assert prompt_env.hash == session_id

    # Ensure the component exists so Environment.load() can load it immediately.
    dp = env[DummyPersistent]

    history = SessionHistory(tmp_path)
    history.load(env)

    assert dp.loaded_value == 'saved'
