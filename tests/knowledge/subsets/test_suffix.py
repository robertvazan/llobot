from pathlib import PurePosixPath
from llobot.knowledge.subsets.suffix import SuffixSubset

def test_suffix_subset():
    subset = SuffixSubset('.txt', '.md')
    assert PurePosixPath('file.txt') in subset
    assert PurePosixPath('document.md') in subset
    assert PurePosixPath('archive.zip') not in subset
    assert PurePosixPath('file.txt.bak') not in subset
