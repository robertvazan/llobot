from pathlib import Path
from llobot.formats.languages.extension import ExtensionLanguageMapping
from llobot.formats.languages.filename import FilenameLanguageMapping
from llobot.formats.languages.union import LanguageMappingUnion

def test_union():
    m1 = FilenameLanguageMapping({'f1': 'lang1'})
    m2 = ExtensionLanguageMapping({'.x': 'lang2'})
    union = LanguageMappingUnion(m1, m2)
    assert union.resolve(Path('f1')) == 'lang1'
    assert union.resolve(Path('f2.x')) == 'lang2'
    assert union.resolve(Path('f3.y')) == ''

def test_or_operator():
    m1 = FilenameLanguageMapping({'f1': 'lang1'})
    m2 = ExtensionLanguageMapping({'.x': 'lang2'})
    union = m1 | m2
    assert isinstance(union, LanguageMappingUnion)
    assert union.resolve(Path('f1')) == 'lang1'
    assert union.resolve(Path('f2.x')) == 'lang2'
