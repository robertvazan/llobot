from __future__ import annotations
from pathlib import PurePosixPath
from llobot.projects.library.predefined import PredefinedProjectLibrary
from llobot.projects.zone import ZoneProject


def test_lookup():
    p1 = ZoneProject('z1')
    p2 = ZoneProject('z2')
    library = PredefinedProjectLibrary({'k1': p1, 'k2': p2})

    assert library.lookup('k1') == [p1]
    assert library.lookup('k2') == [p2]
    assert library.lookup('k3') == []


def test_coercion():
    library = PredefinedProjectLibrary({'k1': 'z1'})
    [p] = library.lookup('k1')
    assert isinstance(p, ZoneProject)
    assert p.zones == {PurePosixPath('z1')}


def test_equality():
    library1 = PredefinedProjectLibrary({'k1': 'z1'})
    library2 = PredefinedProjectLibrary({'k1': 'z1'})
    library3 = PredefinedProjectLibrary({'k1': 'z2'})

    assert library1 == library2
    assert library1 != library3
    assert hash(library1) == hash(library2)
