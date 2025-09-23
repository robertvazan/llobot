from pathlib import Path
from llobot.formats.languages.extension import ExtensionLanguageMapping

def test_resolve():
    mapping = ExtensionLanguageMapping()
    assert mapping.resolve(Path('test.py')) == 'python'
    assert mapping.resolve(Path('test.txt')) == ''
    assert mapping.resolve(Path('test')) == ''

def test_custom_mappings():
    mapping = ExtensionLanguageMapping({'.foo': 'foobar'})
    assert mapping.resolve(Path('test.foo')) == 'foobar'
    assert mapping.resolve(Path('test.py')) == ''
