from llobot.commands.project import handle_project_command
from llobot.environments import Environment
from llobot.environments.projects import ProjectEnv
from llobot.projects.library.predefined import PredefinedProjectLibrary
from llobot.projects.library.union import UnionProjectLibrary
from llobot.projects.marker import MarkerProject

def test_handle_project_command():
    project1 = MarkerProject("proj1")
    project2 = MarkerProject("proj2")
    project3 = MarkerProject("proj1", "proj3") # Shares a prefix with project1

    library = UnionProjectLibrary(
        PredefinedProjectLibrary({'proj1': project1, 'proj2': project2}),
        PredefinedProjectLibrary({'proj1': project3, 'proj3': project3}),
    )
    env = Environment()
    project_env = env[ProjectEnv]
    project_env.configure(library)

    # Handle a key with a single project.
    assert handle_project_command("proj2", env) is True
    assert project_env.selected == [project2]

    # Handle a key with multiple projects. Both should be added.
    # Note: UnionProjectLibrary shadows keys, so only the project from the rightmost library (project3) is found.
    assert handle_project_command("proj1", env) is True
    assert set(project_env.selected) == {project2, project3}

    # Handling an unknown key should not change the selected projects.
    assert handle_project_command("unknown", env) is False
    assert set(project_env.selected) == {project2, project3}

    # Handling a key name that looks like an invalid path should not fail and return False.
    assert handle_project_command("invalid/../zone", env) is False
    assert set(project_env.selected) == {project2, project3}
