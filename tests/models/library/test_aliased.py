import pytest
from tests.models.mock import MockModel
from llobot.models.library.aliased import AliasedModelLibrary

def test_aliased_model_library():
    m1 = MockModel(name='m1')
    m2 = MockModel(name='m2')
    library = AliasedModelLibrary({'alias1': m1, 'alias2': m2})
    assert library.lookup('alias1') is m1
    assert library.lookup('alias2') is m2
    assert library.lookup('m1') is None
    assert library.lookup('alias3') is None

    assert library['alias1'] is m1
    assert library['alias2'] is m2
    with pytest.raises(KeyError):
        _ = library['alias3']
    with pytest.raises(KeyError):
        _ = library['m1']
