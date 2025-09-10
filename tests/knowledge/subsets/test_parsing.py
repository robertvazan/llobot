from pathlib import Path
from llobot.knowledge.subsets.parsing import parse_pattern, parse_subset
from llobot.knowledge.subsets.suffix import SuffixSubset
from llobot.knowledge.subsets.filename import FilenameSubset
from llobot.knowledge.subsets.directory import DirectorySubset
from llobot.knowledge.subsets.pattern import PatternSubset, SimplePatternSubset
from llobot.knowledge.subsets.union import UnionSubset
from llobot.knowledge.subsets.empty import EmptySubset

def test_parse_pattern_empty():
    assert isinstance(parse_pattern(), EmptySubset)

def test_parse_pattern_suffix():
    subset = parse_pattern('*.py')
    assert isinstance(subset, SuffixSubset)
    assert Path('test.py') in subset
    assert Path('test.pyc') not in subset

def test_parse_pattern_filename():
    subset = parse_pattern('README.md')
    assert isinstance(subset, FilenameSubset)
    assert Path('README.md') in subset
    assert Path('a/README.md') in subset
    assert Path('README.txt') not in subset

def test_parse_pattern_directory():
    subset = parse_pattern('src/**')
    assert isinstance(subset, DirectorySubset)
    assert Path('src/main.py') in subset
    assert Path('docs/main.py') not in subset

def test_parse_pattern_simple():
    subset = parse_pattern('docs/*.md')
    assert isinstance(subset, SimplePatternSubset)
    assert Path('docs/index.md') in subset
    assert Path('project/docs/index.md') in subset
    assert Path('docs/sub/index.md') not in subset

def test_parse_pattern_full():
    subset = parse_pattern('**/*.py')
    assert isinstance(subset, PatternSubset)
    assert Path('main.py') in subset
    assert Path('src/main.py') in subset
    assert Path('src/utils/helpers.py') in subset
    assert Path('config.ini') not in subset

def test_parse_pattern_absolute():
    subset = parse_pattern('/src/*.py')
    assert isinstance(subset, PatternSubset)
    assert Path('src/main.py') in subset
    assert Path('main.py') not in subset
    assert Path('src/utils/helpers.py') not in subset

def test_parse_pattern_union_optimized():
    subset = parse_pattern('*.py', '*.java')
    assert isinstance(subset, SuffixSubset)
    assert Path('a.py') in subset
    assert Path('b.java') in subset
    assert Path('c.txt') not in subset

def test_parse_pattern_union_mixed():
    subset = parse_pattern('*.py', 'README.md')
    assert isinstance(subset, UnionSubset)
    assert Path('a.py') in subset
    assert Path('README.md') in subset
    assert Path('b.java') not in subset

def test_parse_subset():
    text = """
    # This is a comment
    *.py
    *.java

    src/**
    """
    subset = parse_subset(text)
    assert Path('main.py') in subset
    assert Path('src/com/example/Main.java') in subset
    assert Path('docs/index.md') not in subset
