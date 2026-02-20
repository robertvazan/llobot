from tests.models.mock import MockModel
from llobot.models.library.empty import EmptyModelLibrary
from llobot.models.library.named import NamedModelLibrary
from llobot.models.library.union import UnionModelLibrary

def test_union_model_library():
    m1 = MockModel('m1')
    m2 = MockModel('m2')
    m3 = MockModel('m3')
    m2_override = MockModel('m2')

    lib1 = NamedModelLibrary(m1, m2)
    lib2 = NamedModelLibrary(m2_override, m3)

    union = UnionModelLibrary(lib1, lib2)
    assert union.lookup('m1') is m1
    assert union.lookup('m2') is m2 # from lib1, first one wins
    assert union.lookup('m3') is m3
    assert union.lookup('m4') is None

def test_union_with_operator():
    m1 = MockModel('m1')
    m2 = MockModel('m2')
    m3 = MockModel('m3')
    m2_override = MockModel('m2')

    lib1 = NamedModelLibrary(m1, m2)
    lib2 = NamedModelLibrary(m2_override, m3)

    union = lib1 | lib2
    assert isinstance(union, UnionModelLibrary)
    assert union.lookup('m1') is m1
    assert union.lookup('m2') is m2
    assert union.lookup('m3') is m3
    assert union.lookup('m4') is None

def test_union_flattening():
    lib1 = NamedModelLibrary(MockModel('m1'))
    lib2 = NamedModelLibrary(MockModel('m2'))
    lib3 = EmptyModelLibrary()

    union1 = UnionModelLibrary(lib1, lib2)
    union2 = UnionModelLibrary(union1, lib3)

    assert len(union2.members) == 3
    assert union2.members == (lib1, lib2, lib3)

    union3 = lib1 | lib2 | lib3
    assert isinstance(union3, UnionModelLibrary)
    assert len(union3.members) == 3
    assert union3.members == (lib1, lib2, lib3)
