from __future__ import annotations
from pathlib import Path
from pytest import raises
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.thread import ChatThread
from llobot.environments import Environment
from llobot.environments.history import SessionHistory
from llobot.environments.persistent import PersistentEnv
from llobot.environments.prompt import PromptEnv, _hash_thread

class DummyPersistent(PersistentEnv):
    """
    A simple persistent component used to verify that SessionHistory
    saves and loads environment state.
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
    # Register persistent component
    env[DummyPersistent]

    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "initial prompt")])
    env[PromptEnv].set(prompt)

    history = SessionHistory(tmp_path)
    history.save(env)

    # Verify file written at path derived from the session ID.
    session_id = _hash_thread(prompt)
    session_dir = tmp_path / session_id
    assert (session_dir / DummyPersistent.filename).exists()

def test_save_cleans_up_existing_session(tmp_path: Path):
    """Ensures existing session directory is cleared before saving."""
    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "initial prompt")])
    session_id = _hash_thread(prompt)
    session_dir = tmp_path / session_id
    session_dir.mkdir(parents=True)
    (session_dir / "garbage.txt").write_text("trash")

    env = Environment()
    env[DummyPersistent]
    env[PromptEnv].set(prompt)

    history = SessionHistory(tmp_path)
    history.save(env)

    assert (session_dir / DummyPersistent.filename).exists()
    assert not (session_dir / "garbage.txt").exists()

def test_load_uses_previous_session_id(tmp_path: Path):
    # Prepare saved state for turn 1
    turn1_prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "Turn 1")])
    session_id = _hash_thread(turn1_prompt)
    session_dir = tmp_path / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    (session_dir / DummyPersistent.filename).write_text('saved', encoding='utf-8')

    # Create environment for turn 2 (continuing from Turn 1)
    env = Environment()
    turn2_prompt = turn1_prompt + ChatMessage(ChatIntent.PROMPT, "Turn 2")
    env[PromptEnv].set(turn2_prompt)

    # Ensure PromptEnv calculated correct previous hash
    assert env[PromptEnv].previous_hash == session_id

    # Load history
    history = SessionHistory(tmp_path)
    history.load(env)

    assert env[DummyPersistent].loaded_value == 'saved'

def test_load_raises_on_missing_history(tmp_path: Path):
    env = Environment()
    # Construct prompt that implies history (two prompts)
    prompt = ChatThread([
        ChatMessage(ChatIntent.PROMPT, "Turn 1"),
        ChatMessage(ChatIntent.PROMPT, "Turn 2")
    ])
    env[PromptEnv].set(prompt)

    history = SessionHistory(tmp_path)

    with raises(FileNotFoundError):
        history.load(env)
