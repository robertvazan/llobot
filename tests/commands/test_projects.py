from llobot.commands.projects import ProjectCommand
from llobot.environments import Environment
from llobot.environments.projects import ProjectEnv
from llobot.projects.dummy import DummyProject
import pytest

def test_project_command():
    project1 = DummyProject("proj1")
    project2 = DummyProject("proj2")

    command = ProjectCommand([project1, project2])
    env = Environment()
    project_env = env[ProjectEnv]

    # Handle a known project.
    assert command.handle("proj1", env) is True
    assert project_env.get() is project1

    # Handling the same project again is fine.
    assert command.handle("proj1", env) is True
    assert project_env.get() is project1

    # Handling another known project should fail because a project is already set.
    with pytest.raises(ValueError, match=f"Project already set to {project1.name}, cannot change to {project2.name}"):
        command.handle("proj2", env)

    # Handling an unknown project should not change the selected project.
    assert command.handle("unknown", env) is False
    assert project_env.get() is project1
