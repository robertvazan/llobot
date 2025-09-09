from llobot.commands.project import ProjectCommand
from llobot.environments import Environment
from llobot.environments.projects import ProjectEnv
from llobot.projects.dummy import DummyProject

def test_project_command():
    project1 = DummyProject("proj1")
    project2 = DummyProject("proj2")

    command = ProjectCommand([project1, project2])
    env = Environment()
    project_env = env[ProjectEnv]

    # Handle a known project.
    assert command.handle("proj1", env) is True
    assert project_env.selected == [project1]

    # Handling the same project again is fine.
    assert command.handle("proj1", env) is True
    assert project_env.selected == [project1]

    # Handling another known project adds it to the list.
    assert command.handle("proj2", env) is True
    assert project_env.selected == [project1, project2]

    # Handling an unknown project should not change the selected projects.
    assert command.handle("unknown", env) is False
    assert project_env.selected == [project1, project2]
