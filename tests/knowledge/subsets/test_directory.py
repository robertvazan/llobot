from pathlib import Path
from llobot.knowledge.subsets.directory import DirectorySubset

def test_directory_subset():
    subset = DirectorySubset('src', 'test')

    assert Path('src/main.py') in subset
    assert Path('src/utils/helpers.py') in subset
    assert Path('test/test_main.py') in subset
    assert Path('docs/index.md') not in subset
    assert Path('main.py') not in subset
