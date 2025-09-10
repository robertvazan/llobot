from pathlib import Path
import pytest
from llobot.utils.zones import (
    Zoning, create_zoning, prefix_zoning, wildcard_zoning, coerce_zoning
)

def test_prefix_zoning():
    zoning = prefix_zoning("/tmp/data")
    assert zoning.resolve("zone1") == Path("/tmp/data/zone1")
    assert zoning["zone2"] == Path("/tmp/data/zone2")

def test_wildcard_zoning():
    zoning = wildcard_zoning("/tmp/data/*/logs")
    assert zoning.resolve("app1") == Path("/tmp/data/app1/logs")
    assert zoning["app2"] == Path("/tmp/data/app2/logs")

    with pytest.raises(ValueError):
        wildcard_zoning("/tmp/data/no-wildcard")

def test_create_zoning():
    zoning = create_zoning(lambda z: Path(f"/var/{z}"))
    assert zoning["log"] == Path("/var/log")

def test_coerce_zoning():
    prefix_path = "/tmp/prefix"
    z_prefix = coerce_zoning(prefix_path)
    assert z_prefix.resolve("zone") == Path("/tmp/prefix/zone")

    wildcard_path = "/tmp/wild/*"
    z_wildcard = coerce_zoning(wildcard_path)
    assert z_wildcard.resolve("zone") == Path("/tmp/wild/zone")

    zoning = prefix_zoning("/tmp")
    assert coerce_zoning(zoning) is zoning

    zoning_instance = Zoning()
    assert coerce_zoning(zoning_instance) is zoning_instance
