from llobot.formats.indexes import standard_index_format
from llobot.formats.indexes.details import DetailsIndexFormat
from llobot.knowledge import Knowledge

def test_standard_index_format():
    formatter = standard_index_format()
    assert isinstance(formatter, DetailsIndexFormat)

def test_render_chat():
    knowledge = Knowledge({'a.txt': ''})
    formatter = standard_index_format()
    chat = formatter.render_chat(knowledge)
    assert len(chat) == 2
    assert 'a.txt' in chat.monolithic()
