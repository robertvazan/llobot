from pathlib import Path
from llobot.knowledge.subsets.empty import EmptySubset

def test_empty_subset():
    subset = EmptySubset()
    assert Path('any/path.txt') not in subset
