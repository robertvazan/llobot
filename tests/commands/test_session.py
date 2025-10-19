from datetime import UTC
from pathlib import Path
from unittest.mock import patch
import pytest
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.commands.session import ensure_session_command, handle_session_command
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.history import SessionHistory
from llobot.environments.session import SessionEnv
from llobot.utils.time import current_time, format_time, parse_time

def test_handle_session_command():
    env = Environment()
    session_env = env[SessionEnv]

    # Valid timestamp
    assert handle_session_command("20240101-120000", env) is True
    assert session_env.get_id() == parse_time("20240101-120000")

    # Invalid timestamp
    assert handle_session_command("not-a-timestamp", env) is False
    assert session_env.get_id() == parse_time("20240101-120000") # Unchanged

    # Setting another valid one fails
    with pytest.raises(ValueError):
        handle_session_command("20240102-120000", env)

def test_ensure_session_command_no_id():
    env = Environment()
    session_env = env[SessionEnv]

    now = current_time()
    with patch('llobot.utils.time.current_time', return_value=now):
        ensure_session_command(env)

    assert session_env.get_id() == now
    assert session_env.content() == f"Session: @{format_time(now)}"

def test_ensure_session_command_with_id():
    env = Environment()
    session_env = env[SessionEnv]
    existing_id = parse_time("20230101-000000")
    session_env.set_id(existing_id)

    ensure_session_command(env)

    assert session_env.get_id() == existing_id
    assert not session_env.content()
