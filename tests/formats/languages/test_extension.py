from pathlib import PurePosixPath
from llobot.formats.languages.extension import ExtensionLanguageMapping

def test_resolve():
    mapping = ExtensionLanguageMapping()
    assert mapping.resolve(PurePosixPath('test.py')) == 'python'
    assert mapping.resolve(PurePosixPath('test.txt')) == ''
    assert mapping.resolve(PurePosixPath('test')) == ''

def test_custom_mappings():
    mapping = ExtensionLanguageMapping({'.foo': 'foobar'})
    assert mapping.resolve(PurePosixPath('test.foo')) == 'foobar'
    assert mapping.resolve(PurePosixPath('test.py')) == ''
