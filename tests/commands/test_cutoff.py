from datetime import datetime, UTC
from unittest.mock import Mock, patch
import pytest
from llobot.commands.cutoff import CutoffCommand, ImplicitCutoffStep
from llobot.environments import Environment
from llobot.environments.cutoff import CutoffEnv
from llobot.environments.projects import ProjectEnv
from llobot.environments.prompt import PromptEnv
from llobot.environments.session import SessionEnv
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

def test_implicit_cutoff_step_no_cutoff_last_prompt():
    archive = Mock(spec=KnowledgeArchive)
    step = ImplicitCutoffStep(archive)
    env = Environment()

    p1 = Mock(spec=Project)
    p1.name = "p1"
    p2 = Mock(spec=Project)
    p2.name = "p2"

    env[ProjectEnv].add(p1)
    env[ProjectEnv].add(p2)
    env[PromptEnv].mark_last()
    cutoff_env = env[CutoffEnv]
    session_env = env[SessionEnv]

    now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
    with patch('llobot.commands.cutoff.current_time', return_value=now):
        step.process(env)

    p1.refresh.assert_called_once_with(archive)
    p2.refresh.assert_called_once_with(archive)
    assert cutoff_env.get() == now
    assert session_env.content() == f"Data cutoff: @{format_time(now)}"

def test_implicit_cutoff_step_no_cutoff_not_last_prompt():
    archive = Mock(spec=KnowledgeArchive)
    step = ImplicitCutoffStep(archive)
    env = Environment()
    project = Mock(spec=Project)
    project.name = "p1"
    env[ProjectEnv].add(project)
    cutoff_env = env[CutoffEnv]
    session_env = env[SessionEnv]

    assert not env[PromptEnv].is_last
    now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
    with patch('llobot.commands.cutoff.current_time', return_value=now):
        step.process(env) # not last, should do nothing

    project.refresh.assert_not_called()
    assert cutoff_env.get() is None
    assert not session_env.content()

def test_implicit_cutoff_step_with_cutoff():
    archive = Mock(spec=KnowledgeArchive)
    step = ImplicitCutoffStep(archive)
    env = Environment()
    project = Mock(spec=Project)
    project.name = "p1"
    env[ProjectEnv].add(project)
    env[PromptEnv].mark_last()
    cutoff_env = env[CutoffEnv]
    session_env = env[SessionEnv]

    existing_cutoff = parse_time("20230101-000000")
    cutoff_env.set(existing_cutoff)

    now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
    with patch('llobot.commands.cutoff.current_time', return_value=now):
        step.process(env)

    project.refresh.assert_not_called()
    assert cutoff_env.get() == existing_cutoff
    assert not session_env.content()

def test_implicit_cutoff_step_no_project():
    archive = Mock(spec=KnowledgeArchive)
    step = ImplicitCutoffStep(archive)
    env = Environment()
    env[PromptEnv].mark_last()
    cutoff_env = env[CutoffEnv]

    now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
    with patch('llobot.commands.cutoff.current_time', return_value=now):
        step.process(env)

    archive.refresh.assert_not_called()
    assert cutoff_env.get() == now

def test_implicit_cutoff_step_no_archive():
    step = ImplicitCutoffStep()
    env = Environment()
    project = Mock(spec=Project)
    project.name = "test-project"
    env[ProjectEnv].add(project)
    env[PromptEnv].mark_last()
    cutoff_env = env[CutoffEnv]
    session_env = env[SessionEnv]

    now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
    with patch('llobot.commands.cutoff.current_time', return_value=now):
        step.process(env)

    assert cutoff_env.get() == now
    assert session_env.content() == f"Data cutoff: @{format_time(now)}"
