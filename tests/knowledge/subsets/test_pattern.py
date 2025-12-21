from pathlib import PurePosixPath
from llobot.knowledge.subsets.pattern import PatternSubset, SimplePatternSubset

def test_pattern_subset():
    subset = PatternSubset('src/**/*.py')
    assert PurePosixPath('src/main.py') in subset
    assert PurePosixPath('src/utils/helpers.py') in subset
    assert PurePosixPath('main.py') not in subset
    assert PurePosixPath('src/config.ini') not in subset

    subset2 = PatternSubset('**/*.py')
    assert PurePosixPath('main.py') in subset2
    assert PurePosixPath('src/main.py') in subset2

    subset3 = PatternSubset('a/b.py')
    assert PurePosixPath('a/b.py') in subset3
    assert PurePosixPath('x/a/b.py') not in subset3

def test_simple_pattern_subset():
    subset = SimplePatternSubset('*.py')
    assert PurePosixPath('a.py') in subset
    assert PurePosixPath('x/y/b.py') in subset
    assert PurePosixPath('a.pyc') not in subset

    subset2 = SimplePatternSubset('test_*.py')
    assert PurePosixPath('test_main.py') in subset2
    assert PurePosixPath('src/test_utils.py') in subset2
    assert PurePosixPath('main_test.py') not in subset2

    subset3 = SimplePatternSubset('docs/*.md')
    assert PurePosixPath('docs/index.md') in subset3
    assert PurePosixPath('docs/sub/index.md') not in subset3
