from pathlib import Path
from llobot.knowledge.subsets.paths import PathsSubset
from llobot.knowledge.indexes import KnowledgeIndex

def test_paths_subset():
    index = KnowledgeIndex([Path('a/b.txt'), Path('c/d.py')])
    subset = PathsSubset(index)
    assert Path('a/b.txt') in subset
    assert Path('c/d.py') in subset
    assert Path('e/f.md') not in subset
