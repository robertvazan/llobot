import pytest
from llobot.models.echo import EchoModel
from llobot.models.library.named import NamedModelLibrary

def test_named_model_library():
    m1 = EchoModel('m1')
    m2 = EchoModel('m2')
    library = NamedModelLibrary(m1, m2)
    assert library.lookup('m1') is m1
    assert library.lookup('m2') is m2
    assert library.lookup('m3') is None

    assert library['m1'] is m1
    assert library['m2'] is m2
    with pytest.raises(KeyError):
        _ = library['m3']

def test_named_model_library_duplicate_name():
    m1a = EchoModel('m1')
    m1b = EchoModel('m1')
    with pytest.raises(ValueError, match="Duplicate model name: m1"):
        NamedModelLibrary(m1a, m1b)
