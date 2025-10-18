from pathlib import Path
from llobot.formats.deltas.granular import GranularKnowledgeDeltaFormat
from llobot.knowledge.deltas.knowledge import KnowledgeDelta
from llobot.knowledge.deltas.documents import DocumentDelta
from llobot.chats.monolithic import monolithic_chat

def test_render_chat_empty():
    formatter = GranularKnowledgeDeltaFormat()
    delta = KnowledgeDelta()
    chat = formatter.render_chat(delta)
    assert not chat

def test_render_chat():
    formatter = GranularKnowledgeDeltaFormat()
    delta = KnowledgeDelta([
        DocumentDelta(Path('a.txt'), 'content a'),
        DocumentDelta(Path('b.txt'), None, removed=True),
    ])
    chat = formatter.render_chat(delta)
    assert len(chat) == 4 # 2 messages + 2 affirmations
    monolithic = monolithic_chat(chat)
    assert 'File: a.txt' in monolithic
    assert 'Removed: `b.txt`' in monolithic
