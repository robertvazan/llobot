from pathlib import Path
from llobot.knowledge.subsets.pattern import PatternSubset, SimplePatternSubset

def test_pattern_subset():
    subset = PatternSubset('src/**/*.py')
    assert Path('src/main.py') in subset
    assert Path('src/utils/helpers.py') in subset
    assert Path('main.py') not in subset
    assert Path('src/config.ini') not in subset

    subset2 = PatternSubset('**/*.py')
    assert Path('main.py') in subset2
    assert Path('src/main.py') in subset2

    subset3 = PatternSubset('a/b.py')
    assert Path('a/b.py') in subset3
    assert Path('x/a/b.py') not in subset3

def test_simple_pattern_subset():
    subset = SimplePatternSubset('*.py')
    assert Path('a.py') in subset
    assert Path('x/y/b.py') in subset
    assert Path('a.pyc') not in subset

    subset2 = SimplePatternSubset('test_*.py')
    assert Path('test_main.py') in subset2
    assert Path('src/test_utils.py') in subset2
    assert Path('main_test.py') not in subset2

    subset3 = SimplePatternSubset('docs/*.md')
    assert Path('docs/index.md') in subset3
    assert Path('docs/sub/index.md') not in subset3
