from llobot.projects.zone import ZoneProject
from llobot.projects.library.zone import ZoneKeyedProjectLibrary

def test_zone_keyed_project_library():
    p1 = ZoneProject('z1')
    p2 = ZoneProject('z2')
    p3 = ZoneProject('z1', 'z3')

    lib = ZoneKeyedProjectLibrary(p1, p2, p3)

    assert set(lib.lookup('z1')) == {p1, p3}
    assert lib.lookup('z2') == [p2]
    assert lib.lookup('z3') == [p3]
    assert lib.lookup('nonexistent') == []
