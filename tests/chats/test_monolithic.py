from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.thread import ChatThread
from llobot.chats.monolithic import monolithic_chat, monolithic_message

def test_monolithic_message():
    """Tests the monolithic string representation of a message."""
    msg = ChatMessage(ChatIntent.PROMPT, "Hello")
    assert monolithic_message(msg) == "**Prompt:**\n\nHello"

def test_monolithic_chat():
    """Tests monolithic string representation of a chat."""
    msg1 = ChatMessage(ChatIntent.PROMPT, "p1")
    msg2 = ChatMessage(ChatIntent.RESPONSE, "r1")
    chat = ChatThread([msg1, msg2])
    expected = "**Prompt:**\n\np1\n\n**Response:**\n\nr1"
    assert monolithic_chat(chat) == expected
