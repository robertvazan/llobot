from llobot.environments.projects import ProjectEnv
from llobot.projects.dummy import DummyProject
from llobot.projects.none import NoProject
from llobot.projects.union import UnionProject

def test_project_env_empty():
    env = ProjectEnv()
    assert env.selected == []
    assert isinstance(env.union, NoProject)

def test_project_env_add_one():
    env = ProjectEnv()
    project = DummyProject('proj')
    env.add(project)
    assert env.selected == [project]
    assert env.union is project

def test_project_env_add_multiple():
    env = ProjectEnv()
    p1 = DummyProject("p1")
    p2 = DummyProject("p2")
    env.add(p2)
    env.add(p1)

    assert env.selected == [p1, p2] # sorted
    union = env.union
    assert isinstance(union, UnionProject)
    assert union._projects == [p1, p2]

def test_project_env_add_replaces():
    env = ProjectEnv()
    p1a = DummyProject("p1")
    p1b = DummyProject("p1")
    env.add(p1a)
    assert env.selected == [p1a]
    env.add(p1b)
    assert env.selected == [p1b]

def test_project_env_union_caching():
    env = ProjectEnv()
    p1 = DummyProject("p1")
    env.add(p1)
    union1 = env.union
    assert union1 is p1
    union2 = env.union
    assert union1 is union2

    p2 = DummyProject("p2")
    env.add(p2)
    union3 = env.union
    assert union3 is not union1
    assert isinstance(union3, UnionProject)
