from llobot.formats.indexes.details import DetailsIndexFormat
from llobot.formats.indexes.flat import FlatIndexFormat
from llobot.knowledge.indexes import KnowledgeIndex

def test_render():
    index = KnowledgeIndex(['a.txt'])
    flat_format = FlatIndexFormat()
    formatter = DetailsIndexFormat(flat_format, title='Test Files')
    result = formatter.render(index)
    assert '<summary>Test Files</summary>' in result
    assert 'a.txt' in result
    assert result.startswith('<details>')
    assert result.endswith('</details>')

def test_render_empty():
    index = KnowledgeIndex()
    flat_format = FlatIndexFormat()
    formatter = DetailsIndexFormat(flat_format, title='Test Files')
    result = formatter.render(index)
    assert result == ''
