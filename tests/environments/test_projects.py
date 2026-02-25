from pathlib import Path, PurePosixPath
import pytest
from llobot.environments.projects import ProjectEnv
from llobot.projects.empty import EmptyProject
from llobot.projects.library.predefined import PredefinedProjectLibrary
from llobot.projects.library.union import UnionProjectLibrary
from llobot.projects.union import UnionProject
from llobot.projects.marker import MarkerProject

def test_project_env_empty():
    env = ProjectEnv()
    assert env.selected == []
    assert isinstance(env.union, EmptyProject)
    assert env.add("any") == []
    assert env.selected == []

def test_project_env_add():
    p1 = MarkerProject("p1")
    p2 = MarkerProject("p2")
    p3 = MarkerProject("p1", "p3")
    library = UnionProjectLibrary(
        PredefinedProjectLibrary({'p1': p1, 'p2': p2}),
        PredefinedProjectLibrary({'p1': p3, 'p3': p3}),
    )

    env = ProjectEnv()
    env.configure(library)

    # Add one project
    found = env.add("p2")
    assert found == [p2]
    assert env.selected == [p2]
    assert env.union is p2

    # Add multiple projects with one key (shadowing)
    found = env.add("p1")
    assert set(found) == {p3}
    assert set(env.selected) == {p2, p3}

    # Add nothing with unknown key
    found = env.add("unknown")
    assert found == []
    assert set(env.selected) == {p2, p3}

    # Add an existing project again, should not change selected projects
    found = env.add("p2")
    assert found == [p2]
    assert set(env.selected) == {p2, p3}

def test_project_env_add_deduplicates():
    p1a = MarkerProject("p1")
    p1b = MarkerProject("p1") # Same value, different object
    library = PredefinedProjectLibrary({'p1': p1a, 'p1_dup': p1b})

    env = ProjectEnv()
    env.configure(library)

    env.add("p1")
    env.add("p1_dup")
    # The set should only contain one of them, as they are equal.
    assert len(env.selected) == 1

def test_project_env_union_caching():
    p1 = MarkerProject("p1")
    p2 = MarkerProject("p2")
    library = PredefinedProjectLibrary({'p1': p1, 'p2': p2})

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

def test_project_env_persistence(tmp_path: Path):
    p1 = MarkerProject("p1")
    p2 = MarkerProject("p2")
    p3 = MarkerProject("p3")
    library = PredefinedProjectLibrary({'p1': p1, 'p2': p2, 'p3': p3})

    # --- Save env with p1, p2 ---
    env1 = ProjectEnv()
    env1.configure(library)
    env1.add("p1")
    env1.add("p2")

    save_path = tmp_path / "env"
    env1.save(save_path)

    projects_txt = save_path / 'projects.txt'
    assert projects_txt.exists()
    assert projects_txt.read_text() == "p1\np2\n"

    # --- Test loading into an env that already has p3, should be cleared ---
    env2 = ProjectEnv()
    env2.configure(library)
    env2.add("p3")
    assert env2._keys == {"p3"}

    env2.load(save_path)

    # State should be replaced with loaded state
    assert env2._keys == {"p1", "p2"}
    assert len(env2.selected) == 2
    # .selected is sorted by prefix
    assert env2.selected[0].prefixes == {PurePosixPath("p1")}
    assert env2.selected[1].prefixes == {PurePosixPath("p2")}

def test_project_env_load_not_found_fails(tmp_path: Path):
    library = PredefinedProjectLibrary({'p1': MarkerProject("p1")})

    save_path = tmp_path / "env"
    save_path.mkdir()
    (save_path / "projects.txt").write_text("p1\np2\n") # p2 does not exist

    env = ProjectEnv()
    env.configure(library)

    with pytest.raises(ValueError, match="Project key 'p2' from projects.txt not found in library."):
        env.load(save_path)

def test_project_env_load_missing_file_clears(tmp_path: Path):
    p1 = MarkerProject("p1")
    library = PredefinedProjectLibrary({'p1': p1})

    env = ProjectEnv()
    env.configure(library)
    env.add("p1")
    assert env._keys == {"p1"}

    # Load from a non-existent dir/file. It should clear the env.
    env.load(tmp_path / "nonexistent")

    assert env._keys == set()
    assert env.selected == []
