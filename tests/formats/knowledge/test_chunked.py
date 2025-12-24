from __future__ import annotations
from pathlib import PurePosixPath
from llobot.chats.intent import ChatIntent
from llobot.knowledge import Knowledge
from llobot.formats.knowledge.chunked import ChunkedKnowledgeFormat

def test_render_chat_single_chunk():
    knowledge = Knowledge({
        PurePosixPath('a.txt'): 'content a',
        PurePosixPath('b.txt'): 'content b',
    })
    fmt = ChunkedKnowledgeFormat(min_size=1000)
    chat = fmt.render_chat(knowledge)
    assert len(chat) == 2 # one affirmation turn
    assert chat[0].intent == ChatIntent.SYSTEM
    assert '<summary>File: ~/a.txt</summary>' in chat[0].content
    assert '<summary>File: ~/b.txt</summary>' in chat[0].content
    assert chat[1].intent == ChatIntent.AFFIRMATION

def test_render_chat_multiple_chunks():
    knowledge = Knowledge({
        PurePosixPath('a.txt'): 'a' * 500,
        PurePosixPath('b.txt'): 'b' * 500,
        PurePosixPath('c.txt'): 'c' * 500,
    })
    fmt = ChunkedKnowledgeFormat(min_size=1000)
    chat = fmt.render_chat(knowledge)
    assert len(chat) == 4 # two affirmation turns
    assert chat[0].intent == ChatIntent.SYSTEM
    assert '<summary>File: ~/a.txt</summary>' in chat[0].content
    assert '<summary>File: ~/b.txt</summary>' in chat[0].content
    assert '<summary>File: ~/c.txt</summary>' not in chat[0].content
    assert chat[2].intent == ChatIntent.SYSTEM
    assert '<summary>File: ~/c.txt</summary>' in chat[2].content

def test_render_chat_empty_knowledge():
    fmt = ChunkedKnowledgeFormat()
    chat = fmt.render_chat(Knowledge())
    assert len(chat) == 0
