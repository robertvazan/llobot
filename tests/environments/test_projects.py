from llobot.environments.projects import ProjectEnv
from llobot.projects import Project
from unittest.mock import Mock
import pytest

def test_project_env():
    env = ProjectEnv()
    assert env.get() is None

    project1 = Mock(spec=Project)
    project1.name = "proj1"

    env.set(project1)
    assert env.get() is project1

    # Setting same project is ok
    env.set(project1)
    assert env.get() is project1

    project2 = Mock(spec=Project)
    project2.name = "proj2"

    with pytest.raises(ValueError):
        env.set(project2)

    assert env.get() is project1
