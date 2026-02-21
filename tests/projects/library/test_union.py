from llobot.projects.library.union import UnionProjectLibrary
from llobot.projects.library.predefined import PredefinedProjectLibrary
from llobot.projects.marker import MarkerProject

def test_union_project_library():
    p1 = MarkerProject('p1')
    p2 = MarkerProject('p2')

    lib1 = PredefinedProjectLibrary({'p1': p1})
    lib2 = PredefinedProjectLibrary({'p2': p2})

    union = UnionProjectLibrary(lib1, lib2)
    # also test operator
    assert (lib1 | lib2) == union

    assert union.lookup('p1') == [p1]
    assert union.lookup('p2') == [p2]

def test_union_project_library_flattening():
    lib1 = PredefinedProjectLibrary({})
    lib2 = PredefinedProjectLibrary({})
    lib3 = PredefinedProjectLibrary({})
    union1 = UnionProjectLibrary(lib1, lib2)
    union2 = UnionProjectLibrary(union1, lib3)
    assert union2._members == (lib1, lib2, lib3)

def test_union_deduplicates():
    p1 = MarkerProject('p1')
    lib1 = PredefinedProjectLibrary({'p1': p1})
    lib2 = PredefinedProjectLibrary({'p1': p1})
    union = UnionProjectLibrary(lib1, lib2)
    assert union.lookup('p1') == [p1]

def test_union_project_library_properties():
    lib1 = PredefinedProjectLibrary({})
    lib2 = PredefinedProjectLibrary({})
    union = UnionProjectLibrary(lib1, lib2)
    assert union.members == (lib1, lib2)
