from pathlib import PurePosixPath
from llobot.formats.languages.filename import FilenameLanguageMapping

def test_resolve():
    mapping = FilenameLanguageMapping()
    assert mapping.resolve(PurePosixPath('Makefile')) == 'makefile'
    assert mapping.resolve(PurePosixPath('Dockerfile')) == 'dockerfile'
    assert mapping.resolve(PurePosixPath('test.py')) == ''

def test_custom_mappings():
    mapping = FilenameLanguageMapping({'foo.bar': 'foobar'})
    assert mapping.resolve(PurePosixPath('foo.bar')) == 'foobar'
    assert mapping.resolve(PurePosixPath('Makefile')) == ''
