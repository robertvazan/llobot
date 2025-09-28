from llobot.projects.library.union import UnionProjectLibrary
from llobot.projects.library.zone import ZoneKeyedProjectLibrary
from llobot.projects.zone import ZoneProject

def test_union_project_library():
    p1 = ZoneProject('p1')
    p2 = ZoneProject('p2')

    lib1 = ZoneKeyedProjectLibrary(p1)
    lib2 = ZoneKeyedProjectLibrary(p2)

    union = UnionProjectLibrary(lib1, lib2)
    # also test operator
    assert (lib1 | lib2) == union

    assert union.lookup('p1') == [p1]
    assert union.lookup('p2') == [p2]

def test_union_project_library_flattening():
    lib1 = ZoneKeyedProjectLibrary()
    lib2 = ZoneKeyedProjectLibrary()
    lib3 = ZoneKeyedProjectLibrary()
    union1 = UnionProjectLibrary(lib1, lib2)
    union2 = UnionProjectLibrary(union1, lib3)
    assert union2._libraries == (lib1, lib2, lib3)

def test_union_deduplicates():
    p1 = ZoneProject('p1')
    lib1 = ZoneKeyedProjectLibrary(p1)
    lib2 = ZoneKeyedProjectLibrary(p1)
    union = UnionProjectLibrary(lib1, lib2)
    assert union.lookup('p1') == [p1]
