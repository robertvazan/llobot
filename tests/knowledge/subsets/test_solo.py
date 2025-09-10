from pathlib import Path
from llobot.knowledge.subsets.solo import SoloSubset

def test_solo_subset():
    path = Path('src/main.py')
    subset = SoloSubset(path)
    assert path in subset
    assert Path('src/test.py') not in subset
