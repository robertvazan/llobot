from llobot.environments.projects import ProjectEnv
from llobot.projects.empty import EmptyProject
from llobot.projects.library.zone import ZoneKeyedProjectLibrary
from llobot.projects.union import UnionProject
from llobot.projects.zone import ZoneProject

def test_project_env_empty():
    env = ProjectEnv()
    assert env.selected == []
    assert isinstance(env.union, EmptyProject)
    assert env.add("any") == []
    assert env.selected == []

def test_project_env_add():
    p1 = ZoneProject("p1")
    p2 = ZoneProject("p2")
    p3 = ZoneProject("p1", "p3")
    library = ZoneKeyedProjectLibrary(p1, p2, p3)

    env = ProjectEnv()
    env.configure(library)

    # Add one project
    found = env.add("p2")
    assert found == [p2]
    assert env.selected == [p2]
    assert env.union is p2

    # Add multiple projects with one key
    found = env.add("p1")
    assert set(found) == {p1, p3}
    assert set(env.selected) == {p1, p2, p3}

    # Add nothing with unknown key
    found = env.add("unknown")
    assert found == []
    assert set(env.selected) == {p1, p2, p3}

    # Add an existing project again, should not change selected projects
    found = env.add("p2")
    assert found == [p2]
    assert set(env.selected) == {p1, p2, p3}

def test_project_env_add_deduplicates():
    p1a = ZoneProject("p1")
    p1b = ZoneProject("p1") # Same value, different object
    library = ZoneKeyedProjectLibrary(p1a, p1b) # library will already deduplicate

    env = ProjectEnv()
    env.configure(library)

    env.add("p1")
    # The set should only contain one of them, as they are equal.
    assert len(env.selected) == 1

def test_project_env_union_caching():
    p1 = ZoneProject("p1")
    p2 = ZoneProject("p2")
    library = ZoneKeyedProjectLibrary(p1, p2)

    env = ProjectEnv()
    env.configure(library)

    env.add("p1")
    union1 = env.union
    assert union1 is p1
    union2 = env.union
    assert union1 is union2

    # add invalidates cache
    env.add("p2")
    union3 = env.union
    assert union3 is not union1
    assert isinstance(union3, UnionProject)
    union4 = env.union
    assert union3 is union4
