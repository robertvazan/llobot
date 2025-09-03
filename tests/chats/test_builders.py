import pytest
from llobot.chats.intents import ChatIntent
from llobot.chats.messages import ChatMessage
from llobot.chats.branches import ChatBranch
from llobot.chats.builders import ChatBuilder

def test_add_message():
    """Tests adding individual ChatMessage objects."""
    builder = ChatBuilder()
    msg1 = ChatMessage(ChatIntent.PROMPT, "p1")
    msg2 = ChatMessage(ChatIntent.RESPONSE, "r1")
    builder.add(msg1)
    builder.add(msg2)
    assert builder.messages == [msg1, msg2]

def test_add_message_merges_same_intent():
    """Tests that adding messages with the same intent merges them."""
    builder = ChatBuilder()
    msg1 = ChatMessage(ChatIntent.PROMPT, "p1")
    msg2 = ChatMessage(ChatIntent.PROMPT, "p2")
    builder.add(msg1)
    builder.add(msg2)
    assert len(builder.messages) == 1
    assert builder[0].intent == ChatIntent.PROMPT
    assert builder[0].content == "p1\n\np2"

def test_add_branch():
    """Tests adding a ChatBranch."""
    builder = ChatBuilder()
    msg1 = ChatMessage(ChatIntent.PROMPT, "p1")
    msg2 = ChatMessage(ChatIntent.RESPONSE, "r1")
    branch = ChatBranch([msg1, msg2])
    builder.add(branch)
    assert builder.messages == [msg1, msg2]

def test_add_intent_and_string():
    """Tests adding intent followed by string content."""
    builder = ChatBuilder()
    builder.add(ChatIntent.PROMPT)
    builder.add("Hello")
    builder.add(" World")
    assert len(builder) == 1
    assert builder[0].intent == ChatIntent.PROMPT
    assert builder[0].content == "Hello\n\n World"

def test_add_none():
    """Tests that adding None has no effect."""
    builder = ChatBuilder()
    builder.add(None)
    assert len(builder) == 0

def test_add_type_error():
    """Tests that adding an invalid type raises TypeError."""
    builder = ChatBuilder()
    with pytest.raises(TypeError):
        builder.add(123)

def test_prepend():
    """Tests prepending messages and branches."""
    builder = ChatBuilder()
    msg1 = ChatMessage(ChatIntent.PROMPT, "p1")
    builder.add(msg1)

    msg0 = ChatMessage(ChatIntent.RESPONSE, "r0")
    builder.prepend(msg0)
    assert builder.messages == [msg0, msg1]

    branch0 = ChatBranch([
        ChatMessage(ChatIntent.SYSTEM, "s-1"),
        ChatMessage(ChatIntent.SYSTEM, "s-2"),
    ])
    builder.prepend(branch0)
    assert builder.messages == [branch0[0], branch0[1], msg0, msg1]

def test_prepend_does_not_merge():
    """Tests that prepend does not merge intents."""
    builder = ChatBuilder()
    builder.add(ChatMessage(ChatIntent.PROMPT, "p1"))
    builder.prepend(ChatMessage(ChatIntent.PROMPT, "p0"))
    assert len(builder) == 2
    assert builder[0].content == "p0"
    assert builder[1].content == "p1"

def test_build():
    """Tests building a ChatBranch from a builder."""
    builder = ChatBuilder()
    msg1 = ChatMessage(ChatIntent.PROMPT, "p1")
    msg2 = ChatMessage(ChatIntent.RESPONSE, "r1")
    builder.add(msg1)
    builder.add(msg2)

    branch = builder.build()
    assert isinstance(branch, ChatBranch)
    assert branch.messages == [msg1, msg2]
