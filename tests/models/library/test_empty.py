import pytest
from llobot.models.library.empty import EmptyModelLibrary

def test_empty_model_library():
    library = EmptyModelLibrary()
    assert library.lookup('any-key') is None
    with pytest.raises(KeyError):
        _ = library['any-key']
