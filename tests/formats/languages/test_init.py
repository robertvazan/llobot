from pathlib import PurePosixPath
from llobot.formats.languages import standard_language_mapping

def test_standard_mapping():
    mapping = standard_language_mapping()
    assert mapping.resolve(PurePosixPath('Makefile')) == 'makefile'
    assert mapping.resolve(PurePosixPath('test.py')) == 'python'
    assert mapping.resolve(PurePosixPath('test')) == ''
