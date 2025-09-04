from datetime import datetime, timedelta, UTC
from unittest.mock import Mock, patch
import pytest
from llobot.time import current_time, format_time
from llobot.environments import Environment
from llobot.environments.cutoffs import CutoffEnv
from llobot.environments.projects import ProjectEnv
from llobot.environments.sessions import SessionEnv
from llobot.projects import Project

def test_cutoff_env_set():
    env = CutoffEnv()
    cutoff1 = current_time()
    env.set(cutoff1)
    # Cannot call get() as it would generate and freeze if _cutoff is None.
    # We must access internal state for this test.
    assert env._cutoff == cutoff1

    # Setting same cutoff is ok
    env.set(cutoff1)
    assert env._cutoff == cutoff1

    cutoff2 = cutoff1 + timedelta(seconds=1)
    with pytest.raises(ValueError):
        env.set(cutoff2)

    assert env._cutoff == cutoff1

def test_cutoff_env_get_preset():
    env = CutoffEnv()
    cutoff = current_time()
    env._cutoff = cutoff
    assert env.get() == cutoff

@patch('llobot.environments.cutoffs.current_time')
def test_cutoff_env_get_generate_no_project(mock_now):
    now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
    mock_now.return_value = now

    full_env = Environment()
    cutoff_env = full_env[CutoffEnv]
    session_env = full_env[SessionEnv]
    session_env.record()

    assert cutoff_env.get() == now
    # It gets called again, but it should return the cached value
    assert cutoff_env.get() == now

    assert session_env.content() == f"Knowledge cutoff: @{format_time(now)}"
    mock_now.assert_called_once()


@patch('llobot.environments.cutoffs.current_time')
def test_cutoff_env_get_generate_with_project(mock_now):
    now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
    mock_now.return_value = now

    project = Mock(spec=Project)
    full_env = Environment()
    full_env[ProjectEnv].set(project)

    cutoff_env = full_env[CutoffEnv]
    session_env = full_env[SessionEnv]
    session_env.record()

    assert cutoff_env.get() == now
    assert cutoff_env.get() == now

    project.refresh.assert_called_once()
    assert session_env.content() == f"Knowledge cutoff: @{format_time(now)}"
    mock_now.assert_called_once()
