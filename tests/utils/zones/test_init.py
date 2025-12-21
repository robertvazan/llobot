from pathlib import Path, PurePosixPath
import pytest
import re
from llobot.utils.zones import Zoning, coerce_zoning, validate_zone
from llobot.utils.zones.prefix import PrefixZoning
from llobot.utils.zones.wildcard import WildcardZoning

def test_coerce_zoning():
    prefix_path = "/tmp/prefix"
    z_prefix = coerce_zoning(prefix_path)
    assert isinstance(z_prefix, PrefixZoning)
    assert z_prefix.resolve(PurePosixPath("zone")) == Path("/tmp/prefix/zone")

    wildcard_path = "/tmp/wild/*"
    z_wildcard = coerce_zoning(wildcard_path)
    assert isinstance(z_wildcard, WildcardZoning)
    assert z_wildcard.resolve(PurePosixPath("zone")) == Path("/tmp/wild/zone")

    zoning = PrefixZoning("/tmp")
    assert coerce_zoning(zoning) is zoning

    zoning_instance = Zoning()
    assert coerce_zoning(zoning_instance) is zoning_instance

def test_validate_zone():
    validate_zone(PurePosixPath("zone1"))
    validate_zone(PurePosixPath("zone1/sub"))
    validate_zone(PurePosixPath("zone-1.2"))
    validate_zone(PurePosixPath("zone_1"))

    with pytest.raises(ValueError, match="Zone must be a relative path"):
        validate_zone(PurePosixPath("/abs/path"))
    with pytest.raises(ValueError, match="Zone must be a non-empty relative path other than '.'"):
        validate_zone(PurePosixPath(""))
    with pytest.raises(ValueError, match="Zone must be a non-empty relative path other than '.'"):
        validate_zone(PurePosixPath("."))
    with pytest.raises(ValueError, match="Zone component cannot be '..'"):
        validate_zone(PurePosixPath(".."))
    with pytest.raises(ValueError, match="Zone component cannot be '..'"):
        validate_zone(PurePosixPath("zone/.."))
    with pytest.raises(ValueError, match=re.escape("Zone component contains invalid characters: 'zone*'")):
        validate_zone(PurePosixPath("zone*"))
    with pytest.raises(ValueError, match=re.escape("Zone component contains invalid characters: 'zo ne'")):
        validate_zone(PurePosixPath("zo ne"))
