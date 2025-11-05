from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.thread import ChatThread
from llobot.formats.monolithic.details import DetailsMonolithicFormat

def test_details_monolithic_single_message_chat():
    """Tests rendering a chat with a single message."""
    formatter = DetailsMonolithicFormat()
    msg = ChatMessage(ChatIntent.PROMPT, "Hello")
    chat = ChatThread([msg])
    expected = "<details>\n<summary>Prompt</summary>\n\nHello\n\n</details>"
    assert formatter.render(chat) == expected

def test_details_monolithic_chat():
    """Tests rendering a chat thread."""
    formatter = DetailsMonolithicFormat()
    msg1 = ChatMessage(ChatIntent.PROMPT, "p1")
    msg2 = ChatMessage(ChatIntent.RESPONSE, "r1")
    chat = ChatThread([msg1, msg2])
    expected = "<details>\n<summary>Prompt</summary>\n\np1\n\n</details>\n\n<details>\n<summary>Response</summary>\n\nr1\n\n</details>"
    assert formatter.render(chat) == expected

def test_details_monolithic_chat_with_empty_message():
    """Tests that empty messages are filtered out."""
    formatter = DetailsMonolithicFormat()
    msg1 = ChatMessage(ChatIntent.PROMPT, "p1")
    msg2 = ChatMessage(ChatIntent.RESPONSE, " \n ")
    msg3 = ChatMessage(ChatIntent.PROMPT, "p2")
    chat = ChatThread([msg1, msg2, msg3])
    expected = "<details>\n<summary>Prompt</summary>\n\np1\n\n</details>\n\n<details>\n<summary>Prompt</summary>\n\np2\n\n</details>"
    assert formatter.render(chat) == expected
