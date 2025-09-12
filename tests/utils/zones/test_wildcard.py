from pathlib import Path
import re
import pytest
from llobot.utils.zones.wildcard import WildcardZoning

def test_wildcard_zoning():
    zoning = WildcardZoning("/tmp/data/*/logs")
    assert zoning.resolve("app1") == Path("/tmp/data/app1/logs")
    assert zoning["app2"] == Path("/tmp/data/app2/logs")

    with pytest.raises(ValueError, match=re.escape("Wildcard pattern must contain '*': /tmp/data/no-wildcard")):
        WildcardZoning("/tmp/data/no-wildcard")

def test_value_semantics():
    zoning1 = WildcardZoning("/tmp/data/*/logs")
    zoning2 = WildcardZoning(Path("/tmp/data/*/logs"))
    assert zoning1 == zoning2
    assert hash(zoning1) == hash(zoning2)

    # Just check that repr doesn't crash. The exact format is not stable.
    repr(zoning1)
