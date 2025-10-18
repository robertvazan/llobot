from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.thread import ChatThread

def test_construction_and_properties():
    """Tests ChatThread construction and basic properties."""
    msg1 = ChatMessage(ChatIntent.PROMPT, "p1")
    msg2 = ChatMessage(ChatIntent.RESPONSE, "r1")
    chat = ChatThread([msg1, msg2])

    assert len(chat) == 2
    assert chat.messages == (msg1, msg2)
    assert bool(chat) is True
    assert chat.cost == msg1.cost + msg2.cost

    empty_chat = ChatThread()
    assert len(empty_chat) == 0
    assert bool(empty_chat) is False

def test_equality_and_hashing():
    """Tests equality and hashing of ChatThread."""
    msg1 = ChatMessage(ChatIntent.PROMPT, "p1")
    msg2 = ChatMessage(ChatIntent.RESPONSE, "r1")
    chat1 = ChatThread([msg1, msg2])
    chat2 = ChatThread([msg1, msg2])
    chat3 = ChatThread([msg1])

    assert chat1 == chat2
    assert chat1 != chat3
    assert len({chat1, chat2, chat3}) == 2

def test_indexing_and_slicing():
    """Tests item access and slicing."""
    msg1 = ChatMessage(ChatIntent.PROMPT, "p1")
    msg2 = ChatMessage(ChatIntent.RESPONSE, "r1")
    msg3 = ChatMessage(ChatIntent.PROMPT, "p2")
    chat = ChatThread([msg1, msg2, msg3])

    assert chat[0] == msg1
    assert chat[-1] == msg3

    slice = chat[1:3]
    assert isinstance(slice, ChatThread)
    assert slice.messages == (msg2, msg3)

def test_iteration_and_containment():
    """Tests iteration and 'in' operator."""
    msg1 = ChatMessage(ChatIntent.PROMPT, "Hello")
    msg2 = ChatMessage(ChatIntent.RESPONSE, "World")
    chat = ChatThread([msg1, msg2])

    assert list(chat) == [msg1, msg2]
    assert "Hello" in chat
    assert "World" in chat
    assert "foo" not in chat

def test_addition():
    """Tests concatenation of threads and messages."""
    msg1 = ChatMessage(ChatIntent.PROMPT, "p1")
    msg2 = ChatMessage(ChatIntent.RESPONSE, "r1")
    chat1 = ChatThread([msg1])
    chat2 = ChatThread([msg2])

    combined = chat1 + chat2
    assert combined.messages == (msg1, msg2)

    combined_with_msg = chat1 + msg2
    assert combined_with_msg.messages == (msg1, msg2)

    combined_with_none = chat1 + None
    assert combined_with_none == chat1

def test_common_prefix():
    """Tests finding the common prefix with the '&' operator."""
    msg1 = ChatMessage(ChatIntent.PROMPT, "p1")
    msg2 = ChatMessage(ChatIntent.RESPONSE, "r1")
    msg3 = ChatMessage(ChatIntent.PROMPT, "p2")
    msg4 = ChatMessage(ChatIntent.PROMPT, "p3")

    chat1 = ChatThread([msg1, msg2, msg3])
    chat2 = ChatThread([msg1, msg2, msg4])
    chat3 = ChatThread([msg1])

    prefix = chat1 & chat2
    assert prefix.messages == (msg1, msg2)

    prefix2 = chat1 & chat3
    assert prefix2.messages == (msg1,)

    prefix3 = chat1 & ChatThread()
    assert len(prefix3) == 0
