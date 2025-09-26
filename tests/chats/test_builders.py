import pytest
from llobot.chats.intents import ChatIntent
from llobot.chats.messages import ChatMessage, MESSAGE_OVERHEAD
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

def test_add_branch():
    """Tests adding a ChatBranch."""
    builder = ChatBuilder()
    msg1 = ChatMessage(ChatIntent.PROMPT, "p1")
    msg2 = ChatMessage(ChatIntent.RESPONSE, "r1")
    branch = ChatBranch([msg1, msg2])
    builder.add(branch)
    assert builder.messages == [msg1, msg2]

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

def test_build():
    """Tests building a ChatBranch from a builder."""
    builder = ChatBuilder()
    msg1 = ChatMessage(ChatIntent.PROMPT, "p1")
    msg2 = ChatMessage(ChatIntent.RESPONSE, "r1")
    builder.add(msg1)
    builder.add(msg2)

    branch = builder.build()
    assert isinstance(branch, ChatBranch)
    assert branch.messages == (msg1, msg2)

def test_budget():
    """Tests budget and unused properties."""
    builder = ChatBuilder()
    assert builder.budget == 0
    assert builder.unused == 0 # No messages, no budget

    builder.budget = 100
    assert builder.budget == 100
    assert builder.unused == 100

    builder.add(ChatMessage(ChatIntent.PROMPT, "12345")) # cost = 5 + 10 = 15
    assert builder.cost == 15
    assert builder.unused == 85

    builder.add(ChatMessage(ChatIntent.RESPONSE, "1234567890")) # cost = 10 + 10 = 20
    assert builder.cost == 35
    assert builder.unused == 65

def test_mark_and_undo():
    """Tests mark and undo functionality."""
    builder = ChatBuilder()
    msg1 = ChatMessage(ChatIntent.PROMPT, "p1")
    msg2 = ChatMessage(ChatIntent.RESPONSE, "r1")
    msg3 = ChatMessage(ChatIntent.PROMPT, "p2")

    builder.add(msg1)
    builder.mark() # mark is at 1
    builder.add(msg2)
    assert builder.messages == [msg1, msg2]

    builder.undo() # reverts to mark at 1
    assert builder.messages == [msg1]

    # Test custom mark with undo(mark)
    mark_pos = len(builder) # mark_pos is 1
    builder.add(msg2)
    builder.add(msg3)
    assert builder.messages == [msg1, msg2, msg3]

    builder.undo(mark_pos)
    assert builder.messages == [msg1]

    # Undo to beginning
    builder.undo(0)
    assert builder.messages == []
