from pathlib import PurePosixPath
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
    assert PurePosixPath('test.py') in subset
    assert PurePosixPath('test.pyc') not in subset

def test_parse_pattern_filename():
    subset = parse_pattern('README.md')
    assert isinstance(subset, FilenameSubset)
    assert PurePosixPath('README.md') in subset
    assert PurePosixPath('a/README.md') in subset
    assert PurePosixPath('README.txt') not in subset

def test_parse_pattern_directory():
    subset = parse_pattern('src/**')
    assert isinstance(subset, DirectorySubset)
    assert PurePosixPath('src/main.py') in subset
    assert PurePosixPath('docs/main.py') not in subset

def test_parse_pattern_simple():
    subset = parse_pattern('docs/*.md')
    assert isinstance(subset, SimplePatternSubset)
    assert PurePosixPath('docs/index.md') in subset
    assert PurePosixPath('project/docs/index.md') in subset
    assert PurePosixPath('docs/sub/index.md') not in subset

def test_parse_pattern_full():
    subset = parse_pattern('**/*.py')
    assert isinstance(subset, PatternSubset)
    assert PurePosixPath('main.py') in subset
    assert PurePosixPath('src/main.py') in subset
    assert PurePosixPath('src/utils/helpers.py') in subset
    assert PurePosixPath('config.ini') not in subset

def test_parse_pattern_absolute():
    subset = parse_pattern('/src/*.py')
    assert isinstance(subset, PatternSubset)
    assert PurePosixPath('src/main.py') in subset
    assert PurePosixPath('main.py') not in subset
    assert PurePosixPath('src/utils/helpers.py') not in subset

def test_parse_pattern_union_optimized():
    subset = parse_pattern('*.py', '*.java')
    assert isinstance(subset, SuffixSubset)
    assert PurePosixPath('a.py') in subset
    assert PurePosixPath('b.java') in subset
    assert PurePosixPath('c.txt') not in subset

def test_parse_pattern_union_mixed():
    subset = parse_pattern('*.py', 'README.md')
    assert isinstance(subset, UnionSubset)
    assert PurePosixPath('a.py') in subset
    assert PurePosixPath('README.md') in subset
    assert PurePosixPath('b.java') not in subset

def test_parse_subset():
    text = """
    # This is a comment
    *.py
    *.java

    src/**
    """
    subset = parse_subset(text)
    assert PurePosixPath('main.py') in subset
    assert PurePosixPath('src/com/example/Main.java') in subset
    assert PurePosixPath('docs/index.md') not in subset
