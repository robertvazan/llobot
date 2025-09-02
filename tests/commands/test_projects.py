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

    # Handle a known project.
    assert command.handle("proj1", env) is True

    # Handling another known project should fail because a project is already set.
    with pytest.raises(ValueError, match=f"Project already set to {project1.name}, cannot change to {project2.name}"):
        command.handle("proj2", env)

    # Getting the project should return the correct one and freeze the environment.
    assert project_env.get() is project1

    # After freezing, setting a project should fail with a different error.
    with pytest.raises(ValueError, match="Project selection is frozen and cannot be changed."):
        command.handle("proj1", env)

    # Handling an unknown project should not change the selected project.
    assert command.handle("unknown", env) is False
    assert project_env.get() is project1 # Unchanged.

    # Test with a new environment to ensure it can select a different project.
    env2 = Environment()
    project_env2 = env2[ProjectEnv]
    assert command.handle("proj2", env2) is True
    assert project_env2.get() is project2
