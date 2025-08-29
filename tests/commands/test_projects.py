from llobot.commands.projects import ProjectCommand
from llobot.environments import Environment
from llobot.environments.projects import ProjectEnv
from llobot.projects import Project
from unittest.mock import Mock
import pytest

def test_project_command():
    project1 = Mock(spec=Project)
    project1.name = "proj1"
    project2 = Mock(spec=Project)
    project2.name = "proj2"

    command = ProjectCommand([project1, project2])
    env = Environment()

    project_env = env[ProjectEnv]
    assert project_env.get() is None

    # Handle a known project
    handled = command.handle("proj1", env)
    assert handled is True
    assert project_env.get() is project1

    # Handle another known project - should fail in env
    with pytest.raises(ValueError):
        command.handle("proj2", env)

    # Handle an unknown project
    handled = command.handle("unknown", env)
    assert handled is False
    assert project_env.get() is project1 # unchanged

    # Test with a new environment
    env2 = Environment()
    project_env2 = env2[ProjectEnv]
    command.handle("proj2", env2)
    assert project_env2.get() is project2
