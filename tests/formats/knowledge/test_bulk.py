from __future__ import annotations
from pathlib import PurePosixPath
from llobot.chats.intent import ChatIntent
from llobot.knowledge import Knowledge
from llobot.formats.knowledge.bulk import BulkKnowledgeFormat

def test_render_chat():
    knowledge = Knowledge({
        PurePosixPath('a.txt'): 'content a',
        PurePosixPath('b.txt'): 'content b',
    })
    fmt = BulkKnowledgeFormat()
    chat = fmt.render_chat(knowledge)
    assert len(chat) == 1
    assert chat[0].intent == ChatIntent.SYSTEM
    assert '<summary>File: ~/a.txt</summary>' in chat[0].content
    assert '<summary>File: ~/b.txt</summary>' in chat[0].content

def test_render_chat_empty_knowledge():
    fmt = BulkKnowledgeFormat()
    chat = fmt.render_chat(Knowledge())
    assert len(chat) == 0
