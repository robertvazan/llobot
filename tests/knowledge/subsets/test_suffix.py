from pathlib import Path
from llobot.knowledge.subsets.suffix import SuffixSubset

def test_suffix_subset():
    subset = SuffixSubset('.txt', '.md')
    assert Path('file.txt') in subset
    assert Path('document.md') in subset
    assert Path('archive.zip') not in subset
    assert Path('file.txt.bak') not in subset
