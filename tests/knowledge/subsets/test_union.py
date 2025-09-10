from pathlib import Path
from llobot.knowledge.subsets.union import UnionSubset
from llobot.knowledge.subsets.suffix import SuffixSubset
from llobot.knowledge.subsets.filename import FilenameSubset

def test_union_subset():
    py_files = SuffixSubset('.py')
    readme_file = FilenameSubset('README.md')
    py_or_readme = UnionSubset(py_files, readme_file)

    assert Path('main.py') in py_or_readme
    assert Path('README.md') in py_or_readme
    assert Path('config.ini') not in py_or_readme
    assert py_or_readme == (py_files | readme_file)
