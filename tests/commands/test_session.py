from datetime import UTC
from pathlib import Path
from unittest.mock import patch
import pytest
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.commands.session import ImplicitSessionStep, SessionCommand, SessionLoadStep
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.history import SessionHistory
from llobot.environments.session import SessionEnv
from llobot.utils.time import current_time, format_time, parse_time

def test_session_command():
    command = SessionCommand()
    env = Environment()
    session_env = env[SessionEnv]

    # Valid timestamp
    assert command.handle("20240101-120000", env) is True
    assert session_env.get_id() == parse_time("20240101-120000")

    # Invalid timestamp
    assert command.handle("not-a-timestamp", env) is False
    assert session_env.get_id() == parse_time("20240101-120000") # Unchanged

    # Setting another valid one fails
    with pytest.raises(ValueError):
        command.handle("20240102-120000", env)

def test_implicit_session_step_no_id():
    step = ImplicitSessionStep()
    env = Environment()
    session_env = env[SessionEnv]

    now = current_time()
    with patch('llobot.utils.time.current_time', return_value=now):
        step.process(env)

    assert session_env.get_id() == now
    assert session_env.content() == f"Session: @{format_time(now)}"

def test_implicit_session_step_with_id():
    step = ImplicitSessionStep()
    env = Environment()
    session_env = env[SessionEnv]
    existing_id = parse_time("20230101-000000")
    session_env.set_id(existing_id)

    step.process(env)

    assert session_env.get_id() == existing_id
    assert not session_env.content()

def test_session_load_step(tmp_path: Path):
    history = SessionHistory(tmp_path / 'sessions')
    step = SessionLoadStep(history)
    env = Environment()
    session_env = env[SessionEnv]
    session_id = current_time()
    session_env.set_id(session_id)

    # Prepare a saved environment with some persistent (ContextEnv) and
    # non-persistent (SessionEnv) state.
    saved_env = Environment()
    saved_context = saved_env[ContextEnv]
    saved_context.add(ChatMessage(ChatIntent.PROMPT, "previous prompt"))
    saved_session = saved_env[SessionEnv]
    saved_session.append("previous session message")
    history.save(session_id, saved_env)

    step.process(env)

    # Check that persistent state (ContextEnv) was loaded correctly.
    context = env[ContextEnv]
    assert context.populated
    thread = context.build()
    assert len(thread) == 1
    assert thread[0].content == "previous prompt"

    # Check that non-persistent state (SessionEnv) was not loaded. The session ID
    # remains, because it was set on the target env before loading and was not
    # overwritten.
    assert session_env.get_id() == session_id
    assert not session_env.populated

def test_session_load_step_no_id():
    history = SessionHistory(Path('/dummy/path'))
    step = SessionLoadStep(history)
    env = Environment()

    # process should not fail if no id is set
    step.process(env)
    assert env[SessionEnv].get_id() is None

def test_session_load_step_no_archive(tmp_path: Path):
    history = SessionHistory(tmp_path / 'sessions')
    step = SessionLoadStep(history)
    env = Environment()
    session_env = env[SessionEnv]
    session_id = current_time()
    session_env.set_id(session_id)

    # No saved environment, should do nothing, but not fail
    step.process(env)
    assert session_env.get_id() == session_id
    assert not session_env.content()
