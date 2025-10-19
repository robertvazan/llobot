from pathlib import Path
from llobot.commands.project import handle_project_command
from llobot.environments import Environment
from llobot.environments.projects import ProjectEnv
from llobot.projects.library.zone import ZoneKeyedProjectLibrary
from llobot.projects.zone import ZoneProject

def test_handle_project_command():
    project1 = ZoneProject("proj1")
    project2 = ZoneProject("proj2")
    project3 = ZoneProject("proj1", "proj3") # Shares a zone with project1

    library = ZoneKeyedProjectLibrary(project1, project2, project3)
    env = Environment()
    project_env = env[ProjectEnv]
    project_env.configure(library)

    # Handle a zone with a single project.
    assert handle_project_command("proj2", env) is True
    assert project_env.selected == [project2]

    # Handle a zone with multiple projects. Both should be added.
    assert handle_project_command("proj1", env) is True
    assert set(project_env.selected) == {project1, project2, project3}

    # Handling an unknown zone should not change the selected projects.
    assert handle_project_command("unknown", env) is False
    assert set(project_env.selected) == {project1, project2, project3}

    # Handling a zone name that looks like an invalid path should not fail and return False.
    assert handle_project_command("invalid/../zone", env) is False
    assert set(project_env.selected) == {project1, project2, project3}
