from llobot.environments.projects import ProjectEnv
from llobot.projects.empty import EmptyProject
from llobot.projects.union import UnionProject
from llobot.projects.zone import ZoneProject

def test_project_env_empty():
    env = ProjectEnv()
    assert env.selected == []
    assert isinstance(env.union, EmptyProject)

def test_project_env_add_one():
    env = ProjectEnv()
    project = ZoneProject('proj')
    env.add(project)
    assert env.selected == [project]
    assert env.union is project

def test_project_env_add_multiple():
    env = ProjectEnv()
    p1 = ZoneProject("p1")
    p2 = ZoneProject("p2")
    env.add(p2)
    env.add(p1)

    # Sorted by zone
    assert env.selected == [p1, p2]
    union = env.union
    assert isinstance(union, UnionProject)
    assert set(union._projects) == {p1, p2}

def test_project_env_add_replaces_by_equality():
    env = ProjectEnv()
    p1a = ZoneProject("p1")
    p1b = ZoneProject("p1") # Same value, different object
    env.add(p1a)
    assert env.selected == [p1a]
    env.add(p1b)
    # The set should only contain one of them, as they are equal.
    assert len(env.selected) == 1

def test_project_env_union_caching():
    env = ProjectEnv()
    p1 = ZoneProject("p1")
    env.add(p1)
    union1 = env.union
    assert union1 is p1
    union2 = env.union
    assert union1 is union2

    p2 = ZoneProject("p2")
    env.add(p2)
    union3 = env.union
    assert union3 is not union1
    assert isinstance(union3, UnionProject)
