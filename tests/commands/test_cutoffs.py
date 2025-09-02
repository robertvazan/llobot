from llobot.commands.projects import ProjectCommand
from llobot.environments import Environment
from llobot.environments.projects import ProjectEnv
from llobot.projects import Project
from unittest.mock import Mock
import pytest

def test_project_command_selection():
    project1 = Mock(spec=Project)
    project1.name = "proj1"
    command = ProjectCommand([project1])
    env = Environment()
    project_env = env[ProjectEnv]

    assert command.handle("proj1", env) is True
    assert project_env._project is project1

def test_project_command_unknown():
    project1 = Mock(spec=Project)
    project1.name = "proj1"
    command = ProjectCommand([project1])
    env = Environment()
    project_env = env[ProjectEnv]

    assert command.handle("unknown", env) is False
    assert project_env._project is None

def test_project_command_change_fails():
    project1 = Mock(spec=Project)
    project1.name = "proj1"
    project2 = Mock(spec=Project)
    project2.name = "proj2"
    command = ProjectCommand([project1, project2])
    env = Environment()

    command.handle("proj1", env)
    with pytest.raises(ValueError, match="Project already set"):
        command.handle("proj2", env)

def test_project_command_frozen_fails():
    project1 = Mock(spec=Project)
    project1.name = "proj1"
    command = ProjectCommand([project1])
    env = Environment()
    project_env = env[ProjectEnv]

    command.handle("proj1", env)
    project_env.get() # freeze
    with pytest.raises(ValueError, match="Project selection is frozen"):
        command.handle("proj1", env)
