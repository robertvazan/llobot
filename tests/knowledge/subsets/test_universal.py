from pathlib import PurePosixPath
from llobot.knowledge.subsets.universal import UniversalSubset

def test_universal_subset():
    subset = UniversalSubset()
    assert PurePosixPath('any/path.txt') in subset
    assert PurePosixPath('another/file.py') in subset
