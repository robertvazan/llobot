from llobot.formats.indexes import standard_index_format
from llobot.formats.indexes.details import DetailsIndexFormat
from llobot.knowledge.indexes import KnowledgeIndex

def test_standard_index_format():
    formatter = standard_index_format()
    assert isinstance(formatter, DetailsIndexFormat)

def test_render_chat():
    index = KnowledgeIndex(['a.txt'])
    formatter = standard_index_format()
    chat = formatter.render_chat(index)
    assert len(chat) == 2
    assert 'a.txt' in chat.monolithic()
