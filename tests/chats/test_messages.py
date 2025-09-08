from llobot.chats.intents import ChatIntent
from llobot.chats.messages import ChatMessage

def test_properties():
    """Tests basic properties of ChatMessage."""
    msg = ChatMessage(ChatIntent.PROMPT, "Hello")
    assert msg.intent == ChatIntent.PROMPT
    assert msg.content == "Hello"
    assert msg.cost == len("Hello") + 10

def test_equality():
    """Tests equality and hashing."""
    msg1 = ChatMessage(ChatIntent.PROMPT, "Hello")
    msg2 = ChatMessage(ChatIntent.PROMPT, "Hello")
    msg3 = ChatMessage(ChatIntent.RESPONSE, "Hello")
    msg4 = ChatMessage(ChatIntent.PROMPT, "World")

    assert msg1 == msg2
    assert msg1 != msg3
    assert msg1 != msg4
    assert len({msg1, msg2, msg3, msg4}) == 3

def test_contains():
    """Tests the 'in' operator."""
    msg = ChatMessage(ChatIntent.PROMPT, "Hello world")
    assert "Hello" in msg
    assert "world" in msg
    assert "foo" not in msg

def test_monolithic():
    """Tests the monolithic string representation."""
    msg = ChatMessage(ChatIntent.PROMPT, "Hello")
    assert msg.monolithic() == "**Prompt:**\n\nHello"
