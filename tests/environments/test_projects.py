from llobot.environments.projects import ProjectEnv
from llobot.projects.dummy import DummyProject
import pytest

def test_project_env_no_project():
    env = ProjectEnv()
    assert env.get() is None
    # Can set project even after get
    project = DummyProject('proj')
    env.set(project)
    assert env.get() is project

def test_project_env_set_then_get():
    env = ProjectEnv()
    project1 = DummyProject("proj1")
    env.set(project1)

    assert env.get() is project1
    # can still set same project
    env.set(project1)
    assert env.get() is project1

    # can set another project with same name
    project1_again = DummyProject("proj1")
    env.set(project1_again)
    assert env.get() is project1_again

def test_project_env_set_multiple_fails():
    env = ProjectEnv()
    project1 = DummyProject("proj1")
    env.set(project1)

    project2 = DummyProject("proj2")
    with pytest.raises(ValueError, match="Project already set"):
        env.set(project2)
    assert env.get() is project1
