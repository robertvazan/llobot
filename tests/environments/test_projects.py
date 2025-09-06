from llobot.environments.projects import ProjectEnv
from llobot.projects import Project
from unittest.mock import Mock
import pytest

def test_project_env_no_project():
    env = ProjectEnv()
    assert env.get() is None
    # Can set project even after get
    project = Mock(spec=Project)
    project.name = 'proj'
    env.set(project)
    assert env.get() is project

def test_project_env_set_then_get():
    env = ProjectEnv()
    project1 = Mock(spec=Project)
    project1.name = "proj1"
    env.set(project1)

    assert env.get() is project1
    # can still set same project
    env.set(project1)
    assert env.get() is project1

def test_project_env_set_multiple_fails():
    env = ProjectEnv()
    project1 = Mock(spec=Project)
    project1.name = "proj1"
    env.set(project1)

    project2 = Mock(spec=Project)
    project2.name = "proj2"
    with pytest.raises(ValueError, match="Project already set"):
        env.set(project2)
    assert env.get() is project1
