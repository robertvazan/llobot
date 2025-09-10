from pathlib import Path
from llobot.knowledge.subsets.intersection import IntersectionSubset
from llobot.knowledge.subsets.suffix import SuffixSubset
from llobot.knowledge.subsets.directory import DirectorySubset

def test_intersection_subset():
    py_files = SuffixSubset('.py')
    src_dir = DirectorySubset('src')

    src_py_files = IntersectionSubset(py_files, src_dir)

    assert Path('src/main.py') in src_py_files
    assert Path('main.py') not in src_py_files
    assert Path('src/config.txt') not in src_py_files
    assert src_py_files == (py_files & src_dir)
