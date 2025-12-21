from pathlib import PurePosixPath
from llobot.knowledge.subsets.intersection import IntersectionSubset
from llobot.knowledge.subsets.suffix import SuffixSubset
from llobot.knowledge.subsets.directory import DirectorySubset

def test_intersection_subset():
    py_files = SuffixSubset('.py')
    src_dir = DirectorySubset('src')

    src_py_files = IntersectionSubset(py_files, src_dir)

    assert PurePosixPath('src/main.py') in src_py_files
    assert PurePosixPath('main.py') not in src_py_files
    assert PurePosixPath('src/config.txt') not in src_py_files
    assert src_py_files == (py_files & src_dir)
