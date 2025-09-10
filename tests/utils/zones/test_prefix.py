from pathlib import Path
import sys
from llobot.utils.zones.prefix import PrefixZoning

def test_prefix_zoning():
    zoning = PrefixZoning("/tmp/data")
    assert zoning.resolve("zone1") == Path("/tmp/data/zone1")
    assert zoning["zone2"] == Path("/tmp/data/zone2")

def test_value_semantics():
    zoning1 = PrefixZoning("/tmp/data")
    zoning2 = PrefixZoning(Path("/tmp/data"))
    assert zoning1 == zoning2
    assert hash(zoning1) == hash(zoning2)

    # The repr depends on the platform's Path class.
    path_class_name = "WindowsPath" if sys.platform == "win32" else "PosixPath"
    expected_repr = f"PrefixZoning(_prefix={path_class_name}('/tmp/data'))"
    assert repr(zoning1) == expected_repr
