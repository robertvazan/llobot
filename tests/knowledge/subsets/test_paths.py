from pathlib import PurePosixPath
from llobot.knowledge.subsets.paths import PathsSubset
from llobot.knowledge.indexes import KnowledgeIndex

def test_paths_subset():
    index = KnowledgeIndex([PurePosixPath('a/b.txt'), PurePosixPath('c/d.py')])
    subset = PathsSubset(index)
    assert PurePosixPath('a/b.txt') in subset
    assert PurePosixPath('c/d.py') in subset
    assert PurePosixPath('e/f.md') not in subset
