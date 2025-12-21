from pathlib import PurePosixPath
from llobot.knowledge.subsets.empty import EmptySubset

def test_empty_subset():
    subset = EmptySubset()
    assert PurePosixPath('any/path.txt') not in subset
