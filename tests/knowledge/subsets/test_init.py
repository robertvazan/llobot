from pathlib import PurePosixPath
from llobot.knowledge.subsets import coerce_subset
from llobot.knowledge.subsets.solo import SoloSubset
from llobot.knowledge.subsets.parsing import parse_pattern
from llobot.knowledge.subsets.paths import PathsSubset
from llobot.knowledge.indexes import KnowledgeIndex

def test_coerce_subset_from_path():
    path = PurePosixPath('a/b.txt')
    subset = coerce_subset(path)
    assert isinstance(subset, SoloSubset)
    assert path in subset
    assert PurePosixPath('c/d.txt') not in subset

def test_coerce_subset_from_str():
    pattern = '*.py'
    subset = coerce_subset(pattern)
    assert PurePosixPath('a.py') in subset
    assert PurePosixPath('b.txt') not in subset

def test_coerce_subset_from_index():
    index = KnowledgeIndex([PurePosixPath('a.txt'), PurePosixPath('b.py')])
    subset = coerce_subset(index)
    assert isinstance(subset, PathsSubset)
    assert PurePosixPath('a.txt') in subset
    assert PurePosixPath('b.py') in subset
    assert PurePosixPath('c.md') not in subset

def test_operators():
    s1 = coerce_subset('a.txt')
    s2 = coerce_subset('b.txt')
    s3 = coerce_subset('*.txt')

    union = s1 | s2
    assert PurePosixPath('a.txt') in union
    assert PurePosixPath('b.txt') in union
    assert PurePosixPath('c.txt') not in union

    intersection = union & s3
    assert PurePosixPath('a.txt') in intersection
    assert PurePosixPath('b.txt') in intersection

    difference = s3 - s1
    assert PurePosixPath('a.txt') not in difference
    assert PurePosixPath('b.txt') in difference
    assert PurePosixPath('c.txt') in difference

    complement = ~s1
    assert PurePosixPath('a.txt') not in complement
    assert PurePosixPath('b.txt') in complement
