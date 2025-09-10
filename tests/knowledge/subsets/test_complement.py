from pathlib import Path
from llobot.knowledge.subsets.complement import ComplementSubset
from llobot.knowledge.subsets.suffix import SuffixSubset

def test_complement_subset():
    py_files = SuffixSubset('.py')
    not_py_files = ComplementSubset(py_files)

    assert Path('test.py') not in not_py_files
    assert Path('test.txt') in not_py_files
    assert not_py_files == ~py_files
