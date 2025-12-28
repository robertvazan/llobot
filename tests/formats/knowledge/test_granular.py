from __future__ import annotations
from pathlib import PurePosixPath
from llobot.chats.intent import ChatIntent
from llobot.knowledge import Knowledge
from llobot.formats.knowledge.granular import GranularKnowledgeFormat

def test_render_chat():
    knowledge = Knowledge({
        PurePosixPath('a.txt'): 'content a',
        PurePosixPath('b.txt'): 'content b',
    })
    fmt = GranularKnowledgeFormat()
    chat = fmt.render_chat(knowledge)
    assert len(chat) == 2
    assert chat[0].intent == ChatIntent.SYSTEM
    assert '<summary>File: ~/a.txt</summary>' in chat[0].content
    assert chat[1].intent == ChatIntent.SYSTEM
    assert '<summary>File: ~/b.txt</summary>' in chat[1].content

def test_render_chat_empty_knowledge():
    fmt = GranularKnowledgeFormat()
    chat = fmt.render_chat(Knowledge())
    assert len(chat) == 0

def test_render_string():
    knowledge = Knowledge({
        PurePosixPath('a.txt'): 'content a',
        PurePosixPath('b.txt'): 'content b',
    })
    fmt = GranularKnowledgeFormat()
    rendered = fmt.render(knowledge)
    assert '<summary>File: ~/a.txt</summary>' in rendered
    assert '<summary>File: ~/b.txt</summary>' in rendered
    assert rendered.count('<details>') == 2
