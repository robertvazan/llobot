import pytest
from llobot.chats.thread import ChatThread
from llobot.chats.builder import ChatBuilder
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage

def test_add_message():
    """Tests adding individual ChatMessage objects."""
    builder = ChatBuilder()
    msg1 = ChatMessage(ChatIntent.PROMPT, "p1")
    msg2 = ChatMessage(ChatIntent.RESPONSE, "r1")
    builder.add(msg1)
    builder.add(msg2)
    assert builder.messages == [msg1, msg2]

def test_add_thread():
    """Tests adding a ChatThread."""
    builder = ChatBuilder()
    msg1 = ChatMessage(ChatIntent.PROMPT, "p1")
    msg2 = ChatMessage(ChatIntent.RESPONSE, "r1")
    chat = ChatThread([msg1, msg2])
    builder.add(chat)
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
    """Tests building a ChatThread from a builder."""
    builder = ChatBuilder()
    msg1 = ChatMessage(ChatIntent.PROMPT, "p1")
    msg2 = ChatMessage(ChatIntent.RESPONSE, "r1")
    builder.add(msg1)
    builder.add(msg2)

    chat = builder.build()
    assert isinstance(chat, ChatThread)
    assert chat.messages == (msg1, msg2)

def test_budget():
    """Tests budget and unused properties."""
    builder = ChatBuilder()
    assert builder.budget == 0
    assert builder.unused == 0 # No messages, no budget

    builder.budget = 100
    assert builder.budget == 100
    assert builder.unused == 100

    builder.add(ChatMessage(ChatIntent.PROMPT, "12345")) # cost = 5 + 4 = 9
    assert builder.cost == 9
    assert builder.unused == 91

    builder.add(ChatMessage(ChatIntent.RESPONSE, "1234567890")) # cost = 10 + 4 = 14
    assert builder.cost == 23
    assert builder.unused == 77

def test_mark_and_undo():
    """Tests mark and undo functionality."""
    builder = ChatBuilder()
    msg1 = ChatMessage(ChatIntent.PROMPT, "p1")
    msg2 = ChatMessage(ChatIntent.RESPONSE, "r1")
    msg3 = ChatMessage(ChatIntent.PROMPT, "p2")

    builder.add(msg1)
    first_mark = builder.mark() # mark is at 1
    assert first_mark == 1

    builder.add(msg2)
    assert builder.messages == [msg1, msg2]

    builder.undo() # reverts to mark at 1
    assert builder.messages == [msg1]

    # Test custom mark with undo(mark)
    manual_mark = len(builder) # manual_mark is 1
    builder.add(msg2)
    builder.add(msg3)
    assert builder.messages == [msg1, msg2, msg3]

    builder.undo(manual_mark)
    assert builder.messages == [msg1]

    # Undo to beginning
    builder.undo(0)
    assert builder.messages == []

    # Test negative mark validation
    with pytest.raises(ValueError):
        builder.undo(-1)

def test_extension():
    """Tests extension functionality."""
    builder = ChatBuilder()
    msg1 = ChatMessage(ChatIntent.PROMPT, "p1")
    msg2 = ChatMessage(ChatIntent.RESPONSE, "r1")
    msg3 = ChatMessage(ChatIntent.PROMPT, "p2")

    builder.add(msg1)
    first_mark = builder.mark()

    builder.add(msg2)
    extension = builder.extension()
    assert extension.messages == (msg2,)

    builder.add(msg3)
    extension_all = builder.extension(first_mark)
    assert extension_all.messages == (msg2, msg3)

    extension_none = builder.extension(len(builder))
    assert len(extension_none) == 0

    # Test negative mark validation
    with pytest.raises(ValueError):
        builder.extension(-1)

def test_record_simple_text_stream():
    """Tests recording a simple stream of text chunks."""
    builder = ChatBuilder()
    stream = iter([ChatIntent.RESPONSE, "Hello world"])
    recorded_stream = builder.record(stream)
    output = "".join(s for s in recorded_stream if isinstance(s, str))
    assert output == "Hello world"
    assert builder.messages == [ChatMessage(ChatIntent.RESPONSE, "Hello world")]


def test_record_empty_stream():
    """Tests recording an empty stream."""
    builder = ChatBuilder()
    stream = iter([])
    list(builder.record(stream))
    assert not builder.messages


def test_record_multiple_messages():
    """Tests recording a stream with multiple messages."""
    builder = ChatBuilder()
    msg1 = ChatMessage(ChatIntent.STATUS, "info")
    msg2 = ChatMessage(ChatIntent.RESPONSE, "OK")
    def source_stream():
        yield from msg1.stream()
        yield from msg2.stream()
    recorded_stream = builder.record(source_stream())
    list(recorded_stream)
    assert builder.messages == [msg1, msg2]


def test_record_stream_is_pass_through():
    """Tests that record() yields exactly what it consumes."""
    builder = ChatBuilder()
    source = [ChatIntent.STATUS, "s1", " and s2", ChatIntent.RESPONSE, "r1"]
    recorded_stream = builder.record(iter(source))
    output_list = list(recorded_stream)
    assert output_list == source
    assert builder.messages == [
        ChatMessage(ChatIntent.STATUS, "s1 and s2"),
        ChatMessage(ChatIntent.RESPONSE, "r1"),
    ]


def test_record_empty_message_in_stream():
    """Tests recording a stream with an empty message."""
    builder = ChatBuilder()
    source = [ChatIntent.STATUS, ChatIntent.RESPONSE, "r1"]
    list(builder.record(iter(source)))
    assert builder.messages == [
        ChatMessage(ChatIntent.STATUS, ""),
        ChatMessage(ChatIntent.RESPONSE, "r1"),
    ]
