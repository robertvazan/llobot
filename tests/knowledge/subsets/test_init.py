from pathlib import Path
from llobot.knowledge.subsets import coerce_subset
from llobot.knowledge.subsets.solo import SoloSubset
from llobot.knowledge.subsets.parsing import parse_pattern
from llobot.knowledge.subsets.paths import PathsSubset
from llobot.knowledge.indexes import KnowledgeIndex

def test_coerce_subset_from_path():
    path = Path('a/b.txt')
    subset = coerce_subset(path)
    assert isinstance(subset, SoloSubset)
    assert path in subset
    assert Path('c/d.txt') not in subset

def test_coerce_subset_from_str():
    pattern = '*.py'
    subset = coerce_subset(pattern)
    assert Path('a.py') in subset
    assert Path('b.txt') not in subset

def test_coerce_subset_from_index():
    index = KnowledgeIndex([Path('a.txt'), Path('b.py')])
    subset = coerce_subset(index)
    assert isinstance(subset, PathsSubset)
    assert Path('a.txt') in subset
    assert Path('b.py') in subset
    assert Path('c.md') not in subset

def test_operators():
    s1 = coerce_subset('a.txt')
    s2 = coerce_subset('b.txt')
    s3 = coerce_subset('*.txt')

    union = s1 | s2
    assert Path('a.txt') in union
    assert Path('b.txt') in union
    assert Path('c.txt') not in union

    intersection = union & s3
    assert Path('a.txt') in intersection
    assert Path('b.txt') in intersection

    difference = s3 - s1
    assert Path('a.txt') not in difference
    assert Path('b.txt') in difference
    assert Path('c.txt') in difference

    complement = ~s1
    assert Path('a.txt') not in complement
    assert Path('b.txt') in complement
