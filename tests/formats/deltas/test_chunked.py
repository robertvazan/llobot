from pathlib import Path
from llobot.formats.deltas.chunked import ChunkedKnowledgeDeltaFormat
from llobot.knowledge.deltas.knowledge import KnowledgeDelta
from llobot.knowledge.deltas.documents import DocumentDelta
from llobot.chats.monolithic import monolithic_chat

def test_render_chat_empty():
    formatter = ChunkedKnowledgeDeltaFormat()
    delta = KnowledgeDelta()
    chat = formatter.render_chat(delta)
    assert not chat

def test_render_chat_single_chunk():
    formatter = ChunkedKnowledgeDeltaFormat(min_size=1000)
    delta = KnowledgeDelta([
        DocumentDelta(Path('a.txt'), 'content a'),
        DocumentDelta(Path('b.txt'), 'content b'),
    ])
    chat = formatter.render_chat(delta)
    assert len(chat) == 2  # message + affirmation
    monolithic = monolithic_chat(chat)
    assert 'File: a.txt' in monolithic
    assert 'File: b.txt' in monolithic

def test_render_chat_multiple_chunks():
    formatter = ChunkedKnowledgeDeltaFormat(min_size=100)
    delta = KnowledgeDelta([
        DocumentDelta(Path('a.txt'), 'a' * 100),
        DocumentDelta(Path('b.txt'), 'b' * 100),
    ])
    chat = formatter.render_chat(delta)
    assert len(chat) == 4 # 2 messages + 2 affirmations
    first_message = chat[0].content
    assert 'File: a.txt' in first_message
    assert 'File: b.txt' not in first_message
    second_message = chat[2].content
    assert 'File: a.txt' not in second_message
    assert 'File: b.txt' in second_message
