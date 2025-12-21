from pathlib import PurePosixPath
from llobot.knowledge.subsets.filename import FilenameSubset

def test_filename_subset():
    subset = FilenameSubset('README.md', 'LICENSE')

    assert PurePosixPath('README.md') in subset
    assert PurePosixPath('docs/README.md') in subset
    assert PurePosixPath('LICENSE') in subset
    assert PurePosixPath('LICENSE.txt') not in subset
    assert PurePosixPath('main.py') not in subset
