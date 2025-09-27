from pathlib import Path
from llobot.utils.zones.prefix import PrefixZoning

def test_prefix_zoning():
    zoning = PrefixZoning("/tmp/data")
    assert zoning.resolve(Path("zone1")) == Path("/tmp/data/zone1")
    assert zoning[Path("zone2")] == Path("/tmp/data/zone2")

def test_prefix_zoning_with_path():
    zoning = PrefixZoning("/tmp/data")
    assert zoning.resolve(Path("zone1/sub")) == Path("/tmp/data/zone1/sub")
    assert zoning[Path("zone2/sub")] == Path("/tmp/data/zone2/sub")

def test_value_semantics():
    zoning1 = PrefixZoning("/tmp/data")
    zoning2 = PrefixZoning(Path("/tmp/data"))
    assert zoning1 == zoning2
    assert hash(zoning1) == hash(zoning2)

    # Just check that repr doesn't crash. The exact format is not stable.
    repr(zoning1)
