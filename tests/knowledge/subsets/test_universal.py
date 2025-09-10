from pathlib import Path
from llobot.knowledge.subsets.universal import UniversalSubset

def test_universal_subset():
    subset = UniversalSubset()
    assert Path('any/path.txt') in subset
    assert Path('another/file.py') in subset
