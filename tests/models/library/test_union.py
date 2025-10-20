from llobot.models.echo import EchoModel
from llobot.models.library.empty import EmptyModelLibrary
from llobot.models.library.named import NamedModelLibrary
from llobot.models.library.union import UnionModelLibrary

def test_union_model_library():
    m1 = EchoModel('m1')
    m2 = EchoModel('m2')
    m3 = EchoModel('m3')
    m2_override = EchoModel('m2')

    lib1 = NamedModelLibrary(m1, m2)
    lib2 = NamedModelLibrary(m2_override, m3)

    union = UnionModelLibrary(lib1, lib2)
    assert union.lookup('m1') is m1
    assert union.lookup('m2') is m2 # from lib1, first one wins
    assert union.lookup('m3') is m3
    assert union.lookup('m4') is None

def test_union_with_operator():
    m1 = EchoModel('m1')
    m2 = EchoModel('m2')
    m3 = EchoModel('m3')
    m2_override = EchoModel('m2')

    lib1 = NamedModelLibrary(m1, m2)
    lib2 = NamedModelLibrary(m2_override, m3)

    union = lib1 | lib2
    assert isinstance(union, UnionModelLibrary)
    assert union.lookup('m1') is m1
    assert union.lookup('m2') is m2
    assert union.lookup('m3') is m3
    assert union.lookup('m4') is None

def test_union_flattening():
    lib1 = NamedModelLibrary(EchoModel('m1'))
    lib2 = NamedModelLibrary(EchoModel('m2'))
    lib3 = EmptyModelLibrary()

    union1 = UnionModelLibrary(lib1, lib2)
    union2 = UnionModelLibrary(union1, lib3)

    assert len(union2._libraries) == 3
    assert union2._libraries == (lib1, lib2, lib3)

    union3 = lib1 | lib2 | lib3
    assert len(union3._libraries) == 3
    assert union3._libraries == (lib1, lib2, lib3)
