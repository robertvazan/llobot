from pathlib import PurePosixPath
from llobot.knowledge.subsets.difference import DifferenceSubset
from llobot.knowledge.subsets.suffix import SuffixSubset
from llobot.knowledge.subsets.filename import FilenameSubset

def test_difference_subset():
    txt_files = SuffixSubset('.txt')
    readme_file = FilenameSubset('README.txt')

    txt_but_not_readme = DifferenceSubset(txt_files, readme_file)

    assert PurePosixPath('file.txt') in txt_but_not_readme
    assert PurePosixPath('README.txt') not in txt_but_not_readme
    assert PurePosixPath('file.md') not in txt_but_not_readme

    assert txt_but_not_readme == (txt_files - readme_file)
