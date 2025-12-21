from pathlib import PurePosixPath
from llobot.knowledge.subsets.directory import DirectorySubset

def test_directory_subset():
    subset = DirectorySubset('src', 'test')

    assert PurePosixPath('src/main.py') in subset
    assert PurePosixPath('src/utils/helpers.py') in subset
    assert PurePosixPath('test/test_main.py') in subset
    assert PurePosixPath('docs/index.md') not in subset
    assert PurePosixPath('main.py') not in subset
