from pathlib import Path
import pytest
import re
from llobot.utils.zones import Zoning, coerce_zoning, validate_zone
from llobot.utils.zones.prefix import PrefixZoning
from llobot.utils.zones.wildcard import WildcardZoning

def test_coerce_zoning():
    prefix_path = "/tmp/prefix"
    z_prefix = coerce_zoning(prefix_path)
    assert isinstance(z_prefix, PrefixZoning)
    assert z_prefix.resolve(Path("zone")) == Path("/tmp/prefix/zone")

    wildcard_path = "/tmp/wild/*"
    z_wildcard = coerce_zoning(wildcard_path)
    assert isinstance(z_wildcard, WildcardZoning)
    assert z_wildcard.resolve(Path("zone")) == Path("/tmp/wild/zone")

    zoning = PrefixZoning("/tmp")
    assert coerce_zoning(zoning) is zoning

    zoning_instance = Zoning()
    assert coerce_zoning(zoning_instance) is zoning_instance

def test_validate_zone():
    validate_zone(Path("zone1"))
    validate_zone(Path("zone1/sub"))
    validate_zone(Path("zone-1.2"))
    validate_zone(Path("zone_1"))

    with pytest.raises(ValueError, match="Zone must be a relative path"):
        validate_zone(Path("/abs/path"))
    with pytest.raises(ValueError, match="Zone must not be empty"):
        validate_zone(Path(""))
    with pytest.raises(ValueError, match="Zone component cannot be '..'"):
        validate_zone(Path(".."))
    with pytest.raises(ValueError, match="Zone component cannot be '..'"):
        validate_zone(Path("zone/.."))
    with pytest.raises(ValueError, match=re.escape("Zone component contains invalid characters: 'zone*'")):
        validate_zone(Path("zone*"))
    with pytest.raises(ValueError, match=re.escape("Zone component contains invalid characters: 'zo ne'")):
        validate_zone(Path("zo ne"))
