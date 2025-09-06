from datetime import datetime, UTC
from unittest.mock import Mock, patch
import pytest
from llobot.commands.cutoffs import CutoffCommand, ImplicitCutoffCommand
from llobot.environments import Environment
from llobot.environments.cutoffs import CutoffEnv
from llobot.environments.projects import ProjectEnv
from llobot.environments.replay import ReplayEnv
from llobot.environments.session_messages import SessionMessageEnv
from llobot.projects import Project
from llobot.time import parse_time, format_time

def test_cutoff_command():
    command = CutoffCommand()
    env = Environment()
    cutoff_env = env[CutoffEnv]

    # Valid timestamp
    assert command.handle("20240101-120000", env) is True
    assert cutoff_env.get() == parse_time("20240101-120000")

    # Invalid timestamp
    assert command.handle("not-a-timestamp", env) is False
    assert cutoff_env.get() == parse_time("20240101-120000") # Unchanged

    # Setting another valid one fails
    with pytest.raises(ValueError):
        command.handle("20240102-120000", env)

def test_implicit_cutoff_command_no_cutoff_recording():
    command = ImplicitCutoffCommand()
    env = Environment()
    project = Mock(spec=Project)
    env[ProjectEnv].set(project)
    env[ReplayEnv].start_recording()
    cutoff_env = env[CutoffEnv]
    session_env = env[SessionMessageEnv]

    now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
    with patch('llobot.commands.cutoffs.current_time', return_value=now):
        command.process(env)

    project.refresh.assert_called_once()
    assert cutoff_env.get() == now
    assert session_env.content() == f"Cutoff: @{format_time(now)}"

def test_implicit_cutoff_command_no_cutoff_replaying():
    command = ImplicitCutoffCommand()
    env = Environment()
    project = Mock(spec=Project)
    env[ProjectEnv].set(project)
    cutoff_env = env[CutoffEnv]
    session_env = env[SessionMessageEnv]

    now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
    with patch('llobot.commands.cutoffs.current_time', return_value=now):
        command.process(env) # not recording, should do nothing

    project.refresh.assert_not_called()
    assert cutoff_env.get() is None
    assert not session_env.content()

def test_implicit_cutoff_command_with_cutoff():
    command = ImplicitCutoffCommand()
    env = Environment()
    project = Mock(spec=Project)
    env[ProjectEnv].set(project)
    env[ReplayEnv].start_recording()
    cutoff_env = env[CutoffEnv]
    session_env = env[SessionMessageEnv]

    existing_cutoff = parse_time("20230101-000000")
    cutoff_env.set(existing_cutoff)

    now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
    with patch('llobot.commands.cutoffs.current_time', return_value=now):
        command.process(env)

    project.refresh.assert_not_called()
    assert cutoff_env.get() == existing_cutoff
    assert not session_env.content()

def test_implicit_cutoff_command_no_project():
    command = ImplicitCutoffCommand()
    env = Environment()
    env[ReplayEnv].start_recording()
    cutoff_env = env[CutoffEnv]

    now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
    with patch('llobot.commands.cutoffs.current_time', return_value=now):
        command.process(env)

    assert cutoff_env.get() == now
