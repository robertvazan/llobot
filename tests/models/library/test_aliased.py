import pytest
from llobot.models.echo import EchoModel
from llobot.models.library.aliased import AliasedModelLibrary

def test_aliased_model_library():
    m1 = EchoModel('m1')
    m2 = EchoModel('m2')
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
