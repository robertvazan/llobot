from __future__ import annotations
from pathlib import Path
from llobot.chats.intent import ChatIntent
from llobot.knowledge import Knowledge
from llobot.formats.knowledge.granular import GranularKnowledgeFormat

def test_render_chat():
    knowledge = Knowledge({
        Path('a.txt'): 'content a',
        Path('b.txt'): 'content b',
    })
    fmt = GranularKnowledgeFormat()
    chat = fmt.render_chat(knowledge)
    assert len(chat) == 4 # two affirmation turns
    assert chat[0].intent == ChatIntent.SYSTEM
    assert '<summary>File: a.txt</summary>' in chat[0].content
    assert chat[1].intent == ChatIntent.AFFIRMATION
    assert chat[2].intent == ChatIntent.SYSTEM
    assert '<summary>File: b.txt</summary>' in chat[2].content
    assert chat[3].intent == ChatIntent.AFFIRMATION

def test_render_chat_empty_knowledge():
    fmt = GranularKnowledgeFormat()
    chat = fmt.render_chat(Knowledge())
    assert len(chat) == 0

def test_render_string():
    knowledge = Knowledge({
        Path('a.txt'): 'content a',
        Path('b.txt'): 'content b',
    })
    fmt = GranularKnowledgeFormat()
    rendered = fmt.render(knowledge)
    assert '<summary>File: a.txt</summary>' in rendered
    assert '<summary>File: b.txt</summary>' in rendered
    assert rendered.count('<details>') == 2
