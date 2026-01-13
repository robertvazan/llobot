import pytest
from tests.mock_model import MockModel
from llobot.models.library.named import NamedModelLibrary

def test_named_model_library():
    m1 = MockModel('m1')
    m2 = MockModel('m2')
    library = NamedModelLibrary(m1, m2)
    assert library.lookup('m1') is m1
    assert library.lookup('m2') is m2
    assert library.lookup('m3') is None

    assert library['m1'] is m1
    assert library['m2'] is m2
    with pytest.raises(KeyError):
        _ = library['m3']

def test_named_model_library_duplicate_name():
    m1a = MockModel('m1')
    m1b = MockModel('m1')
    with pytest.raises(ValueError, match="Duplicate model name: m1"):
        NamedModelLibrary(m1a, m1b)
