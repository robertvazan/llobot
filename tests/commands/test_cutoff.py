from datetime import datetime, UTC
from pathlib import Path
from unittest.mock import Mock, patch
import pytest
from llobot.commands.cutoff import CutoffCommand, ImplicitCutoffStep
from llobot.environments import Environment
from llobot.environments.cutoff import CutoffEnv
from llobot.environments.projects import ProjectEnv
from llobot.environments.prompt import PromptEnv
from llobot.environments.session import SessionEnv
from llobot.knowledge import Knowledge
from llobot.knowledge.archives.tgz import TgzKnowledgeArchive
from llobot.projects.directory import DirectoryProject
from llobot.utils.time import parse_time, format_time

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

def test_implicit_cutoff_step_no_cutoff_last_prompt(tmp_path: Path):
    archive = TgzKnowledgeArchive(tmp_path / 'archive')
    step = ImplicitCutoffStep(archive)
    env = Environment()

    p1_path = tmp_path / 'p1'
    p1_path.mkdir()
    (p1_path / 'f.txt').write_text('p1-content')
    p1 = DirectoryProject(p1_path)

    p2_path = tmp_path / 'p2'
    p2_path.mkdir()
    (p2_path / 'f.txt').write_text('p2-content')
    p2 = DirectoryProject(p2_path)

    env[ProjectEnv].add(p1)
    env[ProjectEnv].add(p2)
    env[PromptEnv].mark_last()
    cutoff_env = env[CutoffEnv]
    session_env = env[SessionEnv]

    now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
    with patch('llobot.commands.cutoff.current_time', return_value=now):
        step.process(env)

    assert len(list((tmp_path / 'archive' / p1.prefixes.copy().pop()).iterdir())) == 1
    assert len(list((tmp_path / 'archive' / p2.prefixes.copy().pop()).iterdir())) == 1
    assert cutoff_env.get() == now
    assert session_env.content() == f"Data cutoff: @{format_time(now)}"

def test_implicit_cutoff_step_no_cutoff_not_last_prompt(tmp_path: Path):
    archive_dir = tmp_path / 'archive'
    archive = TgzKnowledgeArchive(archive_dir)
    step = ImplicitCutoffStep(archive)
    env = Environment()
    p1_path = tmp_path / 'p1'
    p1_path.mkdir()
    p1 = DirectoryProject(p1_path)
    env[ProjectEnv].add(p1)
    cutoff_env = env[CutoffEnv]
    session_env = env[SessionEnv]

    assert not env[PromptEnv].is_last
    now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
    with patch('llobot.commands.cutoff.current_time', return_value=now):
        step.process(env) # not last, should do nothing

    assert not archive_dir.exists()
    assert cutoff_env.get() is None
    assert not session_env.content()

def test_implicit_cutoff_step_with_cutoff(tmp_path: Path):
    archive_dir = tmp_path / 'archive'
    archive = TgzKnowledgeArchive(archive_dir)
    step = ImplicitCutoffStep(archive)
    env = Environment()
    p1_path = tmp_path / 'p1'
    p1_path.mkdir()
    p1 = DirectoryProject(p1_path)
    env[ProjectEnv].add(p1)
    env[PromptEnv].mark_last()
    cutoff_env = env[CutoffEnv]
    session_env = env[SessionEnv]

    existing_cutoff = parse_time("20230101-000000")
    cutoff_env.set(existing_cutoff)

    now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
    with patch('llobot.commands.cutoff.current_time', return_value=now):
        step.process(env)

    assert not archive_dir.exists()
    assert cutoff_env.get() == existing_cutoff
    assert not session_env.content()

def test_implicit_cutoff_step_no_project(tmp_path: Path):
    archive = TgzKnowledgeArchive(tmp_path)
    step = ImplicitCutoffStep(archive)
    env = Environment()
    env[PromptEnv].mark_last()
    cutoff_env = env[CutoffEnv]

    now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
    with patch('llobot.commands.cutoff.current_time', return_value=now):
        step.process(env)

    # No project means EmptyProject, which has no prefixes and refresh is a no-op
    assert cutoff_env.get() == now

def test_implicit_cutoff_step_no_archive(tmp_path: Path):
    step = ImplicitCutoffStep()
    env = Environment()
    p_path = tmp_path / 'p'
    p_path.mkdir()
    project = DirectoryProject(p_path)
    env[ProjectEnv].add(project)
    env[PromptEnv].mark_last()
    cutoff_env = env[CutoffEnv]
    session_env = env[SessionEnv]

    now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
    with patch('llobot.commands.cutoff.current_time', return_value=now):
        step.process(env)

    assert cutoff_env.get() == now
    assert session_env.content() == f"Data cutoff: @{format_time(now)}"
