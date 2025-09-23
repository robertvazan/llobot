from pathlib import Path
from llobot.formats.languages import standard_language_mapping

def test_standard_mapping():
    mapping = standard_language_mapping()
    assert mapping.resolve(Path('Makefile')) == 'makefile'
    assert mapping.resolve(Path('test.py')) == 'python'
    assert mapping.resolve(Path('test')) == ''
