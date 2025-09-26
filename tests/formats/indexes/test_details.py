from llobot.formats.indexes.details import DetailsIndexFormat
from llobot.formats.indexes.flat import FlatIndexFormat
from llobot.knowledge import Knowledge

def test_render():
    knowledge = Knowledge({'a.txt': ''})
    flat_format = FlatIndexFormat()
    formatter = DetailsIndexFormat(flat_format, title='Test Files')
    result = formatter.render(knowledge)
    assert '<summary>Test Files</summary>' in result
    assert 'a.txt' in result
    assert result.startswith('<details>')
    assert result.endswith('</details>')

def test_render_empty():
    knowledge = Knowledge()
    flat_format = FlatIndexFormat()
    formatter = DetailsIndexFormat(flat_format, title='Test Files')
    result = formatter.render(knowledge)
    assert result == ''
