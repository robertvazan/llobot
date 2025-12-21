from pathlib import PurePosixPath
from llobot.knowledge.subsets.solo import SoloSubset

def test_solo_subset():
    path = PurePosixPath('src/main.py')
    subset = SoloSubset(path)
    assert path in subset
    assert PurePosixPath('src/test.py') not in subset
