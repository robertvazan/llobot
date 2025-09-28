from pathlib import Path
from llobot.commands.project import ProjectCommand
from llobot.environments import Environment
from llobot.environments.projects import ProjectEnv
from llobot.projects.library.zone import ZoneKeyedProjectLibrary
from llobot.projects.zone import ZoneProject

def test_project_command():
    project1 = ZoneProject("proj1")
    project2 = ZoneProject("proj2")
    project3 = ZoneProject("proj1", "proj3") # Shares a zone with project1

    library = ZoneKeyedProjectLibrary(project1, project2, project3)
    command = ProjectCommand(library)
    env = Environment()
    project_env = env[ProjectEnv]

    # Handle a zone with a single project.
    assert command.handle("proj2", env) is True
    assert project_env.selected == [project2]

    # Handle a zone with multiple projects. Both should be added.
    assert command.handle("proj1", env) is True
    assert set(project_env.selected) == {project1, project2, project3}

    # Handling an unknown zone should not change the selected projects.
    assert command.handle("unknown", env) is False
    assert set(project_env.selected) == {project1, project2, project3}

    # Handling a zone name that looks like an invalid path should not fail and return False.
    assert command.handle("invalid/../zone", env) is False
    assert set(project_env.selected) == {project1, project2, project3}
