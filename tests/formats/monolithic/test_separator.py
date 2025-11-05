from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.thread import ChatThread
from llobot.formats.monolithic.separator import SeparatorMonolithicFormat

def test_separator_monolithic_single_message_chat():
    """Tests rendering a chat with a single message."""
    formatter = SeparatorMonolithicFormat()
    msg = ChatMessage(ChatIntent.PROMPT, "Hello")
    chat = ChatThread([msg])
    assert formatter.render(chat) == "Hello"

def test_separator_monolithic_chat():
    """Tests rendering a chat thread."""
    formatter = SeparatorMonolithicFormat()
    msg1 = ChatMessage(ChatIntent.PROMPT, "p1")
    msg2 = ChatMessage(ChatIntent.RESPONSE, "r1")
    chat = ChatThread([msg1, msg2])
    expected = "p1\n\n---\n\nr1"
    assert formatter.render(chat) == expected

def test_separator_monolithic_chat_with_empty_message():
    """Tests that empty messages are filtered out."""
    formatter = SeparatorMonolithicFormat()
    msg1 = ChatMessage(ChatIntent.PROMPT, "p1")
    msg2 = ChatMessage(ChatIntent.RESPONSE, " ")
    msg3 = ChatMessage(ChatIntent.PROMPT, "p2")
    chat = ChatThread([msg1, msg2, msg3])
    expected = "p1\n\n---\n\np2"
    assert formatter.render(chat) == expected
