from pathlib import Path
from llobot.utils.zones import Zoning, coerce_zoning
from llobot.utils.zones.prefix import PrefixZoning
from llobot.utils.zones.wildcard import WildcardZoning

def test_coerce_zoning():
    prefix_path = "/tmp/prefix"
    z_prefix = coerce_zoning(prefix_path)
    assert isinstance(z_prefix, PrefixZoning)
    assert z_prefix.resolve("zone") == Path("/tmp/prefix/zone")

    wildcard_path = "/tmp/wild/*"
    z_wildcard = coerce_zoning(wildcard_path)
    assert isinstance(z_wildcard, WildcardZoning)
    assert z_wildcard.resolve("zone") == Path("/tmp/wild/zone")

    zoning = PrefixZoning("/tmp")
    assert coerce_zoning(zoning) is zoning

    zoning_instance = Zoning()
    assert coerce_zoning(zoning_instance) is zoning_instance
