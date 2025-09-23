from pathlib import Path
from llobot.formats.languages.filename import FilenameLanguageMapping

def test_resolve():
    mapping = FilenameLanguageMapping()
    assert mapping.resolve(Path('Makefile')) == 'makefile'
    assert mapping.resolve(Path('Dockerfile')) == 'dockerfile'
    assert mapping.resolve(Path('test.py')) == ''

def test_custom_mappings():
    mapping = FilenameLanguageMapping({'foo.bar': 'foobar'})
    assert mapping.resolve(Path('foo.bar')) == 'foobar'
    assert mapping.resolve(Path('Makefile')) == ''
