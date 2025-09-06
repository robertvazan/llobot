from datetime import datetime, UTC
from unittest.mock import Mock, patch
import pytest
from llobot.commands.cutoffs import CutoffCommand, ImplicitCutoffStep
from llobot.environments import Environment
from llobot.environments.cutoffs import CutoffEnv
from llobot.environments.projects import ProjectEnv
from llobot.environments.replay import ReplayEnv
from llobot.environments.session_messages import SessionMessageEnv
from llobot.knowledge import Knowledge
from llobot.knowledge.archives import KnowledgeArchive
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

def test_implicit_cutoff_step_no_cutoff_recording():
    archive = Mock(spec=KnowledgeArchive)
    step = ImplicitCutoffStep(archive)
    env = Environment()
    project = Mock(spec=Project)
    project.name = "test-project"
    mock_knowledge = Knowledge({'a': 'b'})
    project.load.return_value = mock_knowledge
    env[ProjectEnv].set(project)
    env[ReplayEnv].start_recording()
    cutoff_env = env[CutoffEnv]
    session_env = env[SessionMessageEnv]

    now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
    with patch('llobot.commands.cutoffs.current_time', return_value=now):
        step.process(env)

    project.load.assert_called_once()
    archive.refresh.assert_called_once_with(project.name, mock_knowledge)
    assert cutoff_env.get() == now
    assert session_env.content() == f"Cutoff: @{format_time(now)}"

def test_implicit_cutoff_step_no_cutoff_replaying():
    archive = Mock(spec=KnowledgeArchive)
    step = ImplicitCutoffStep(archive)
    env = Environment()
    project = Mock(spec=Project)
    env[ProjectEnv].set(project)
    cutoff_env = env[CutoffEnv]
    session_env = env[SessionMessageEnv]

    now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
    with patch('llobot.commands.cutoffs.current_time', return_value=now):
        step.process(env) # not recording, should do nothing

    project.load.assert_not_called()
    archive.refresh.assert_not_called()
    assert cutoff_env.get() is None
    assert not session_env.content()

def test_implicit_cutoff_step_with_cutoff():
    archive = Mock(spec=KnowledgeArchive)
    step = ImplicitCutoffStep(archive)
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
        step.process(env)

    project.load.assert_not_called()
    archive.refresh.assert_not_called()
    assert cutoff_env.get() == existing_cutoff
    assert not session_env.content()

def test_implicit_cutoff_step_no_project():
    archive = Mock(spec=KnowledgeArchive)
    step = ImplicitCutoffStep(archive)
    env = Environment()
    env[ReplayEnv].start_recording()
    cutoff_env = env[CutoffEnv]

    now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
    with patch('llobot.commands.cutoffs.current_time', return_value=now):
        step.process(env)

    archive.refresh.assert_not_called()
    assert cutoff_env.get() == now

def test_implicit_cutoff_step_no_archive():
    step = ImplicitCutoffStep()
    env = Environment()
    project = Mock(spec=Project)
    project.name = "test-project"
    env[ProjectEnv].set(project)
    env[ReplayEnv].start_recording()
    cutoff_env = env[CutoffEnv]
    session_env = env[SessionMessageEnv]

    now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
    with patch('llobot.commands.cutoffs.current_time', return_value=now):
        step.process(env)

    project.load.assert_not_called()
    assert cutoff_env.get() == now
    assert session_env.content() == f"Cutoff: @{format_time(now)}"
