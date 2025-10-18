import pytest
from llobot.chats.stream import buffer_stream
from llobot.chats.intent import ChatIntent

def test_buffer():
    """
    Tests that the buffer consumes the stream in a background thread.
    """
    def producer_stream():
        # This will run in a worker thread.
        yield "one"
        yield "two"

    stream = buffer_stream(producer_stream())
    assert list(stream) == ["one", "two"]

def test_buffer_multimessage():
    """
    Tests that the buffer can handle a multi-message stream.
    """
    def producer_stream():
        yield ChatIntent.RESPONSE
        yield "message one"
        yield ChatIntent.AFFIRMATION
        yield "message two"
        yield " part two"

    stream = buffer_stream(producer_stream())
    assert list(stream) == [
        ChatIntent.RESPONSE,
        "message one",
        ChatIntent.AFFIRMATION,
        "message two",
        " part two",
    ]

def test_buffer_exception():
    def failing_stream():
        yield "one"
        raise ValueError("test error")

    stream = buffer_stream(failing_stream())
    iterator = iter(stream)
    assert next(iterator) == "one"
    with pytest.raises(ValueError, match="test error"):
        next(iterator)
