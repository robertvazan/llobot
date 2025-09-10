from pathlib import Path
from llobot.knowledge.subsets.filename import FilenameSubset

def test_filename_subset():
    subset = FilenameSubset('README.md', 'LICENSE')

    assert Path('README.md') in subset
    assert Path('docs/README.md') in subset
    assert Path('LICENSE') in subset
    assert Path('LICENSE.txt') not in subset
    assert Path('main.py') not in subset
