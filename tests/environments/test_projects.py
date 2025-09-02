from llobot.environments.projects import ProjectEnv
from llobot.projects import Project
from unittest.mock import Mock
import pytest

def test_project_env_no_project():
    env = ProjectEnv()
    assert env.get() is None
    # after first get(), it's frozen
    with pytest.raises(ValueError, match="Project selection is frozen"):
        env.set(Mock(spec=Project))

def test_project_env_set_then_get():
    env = ProjectEnv()
    project1 = Mock(spec=Project)
    project1.name = "proj1"
    env.set(project1)

    # get freezes it
    assert env.get() is project1

    # cannot set after get
    with pytest.raises(ValueError, match="Project selection is frozen"):
        env.set(project1)

def test_project_env_set_multiple():
    env = ProjectEnv()
    project1 = Mock(spec=Project)
    project1.name = "proj1"

    env.set(project1)
    # Setting same project is ok before get()
    env.set(project1)

    project2 = Mock(spec=Project)
    project2.name = "proj2"

    with pytest.raises(ValueError, match="Project already set"):
        env.set(project2)

    assert env.get() is project1
