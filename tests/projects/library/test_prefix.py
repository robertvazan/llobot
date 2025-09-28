from pathlib import Path
import pytest
from llobot.projects.directory import DirectoryProject
from llobot.projects.library.prefix import PrefixKeyedProjectLibrary
from llobot.projects.zone import ZoneProject

def test_prefix_keyed_project_library(tmp_path: Path):
    p1 = DirectoryProject(tmp_path / 'p1', prefix='p1', zones={'z1'})
    p2 = DirectoryProject(tmp_path / 'p2', prefix='p2', zones={'z2'})
    p3 = DirectoryProject(tmp_path / 'p3', prefix='p1.alt', zones={'z3'})

    lib = PrefixKeyedProjectLibrary(p1, p2, p3)

    assert lib.lookup('p1') == [p1]
    assert lib.lookup('p2') == [p2]
    assert lib.lookup('p1.alt') == [p3]
    assert lib.lookup('nonexistent') == []

def test_prefix_keyed_project_library_prefix_constraints(tmp_path: Path):
    p_no_prefix = ZoneProject('z')
    assert not p_no_prefix.prefixes
    with pytest.raises(ValueError, match="must have at least one prefix"):
        PrefixKeyedProjectLibrary(p_no_prefix)

    p1 = DirectoryProject(tmp_path / 'p1', prefix='p1', zones={'z1'})
    p2 = DirectoryProject(tmp_path / 'p2', prefix='p1', zones={'z2'})  # shared prefix
    with pytest.raises(ValueError, match="Duplicate prefix 'p1'"):
        PrefixKeyedProjectLibrary(p1, p2)
