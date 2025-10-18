import pytest
from llobot.models.streams import text_stream, ok_stream, error_stream, exception_stream, buffer_stream
from llobot.chats.intent import ChatIntent

def test_text_stream():
    stream = text_stream("This is a test.")
    chunks = list(stream)
    assert chunks == ["This is a test."]
    assert "".join(text_stream("This is a test.")) == "This is a test."

def test_text_stream_empty():
    stream = text_stream("")
    chunks = list(stream)
    assert not chunks
    assert "".join(text_stream("")) == ""

def test_ok_error_streams():
    assert "".join(text_stream("Ready.")) == "Ready."
    assert "".join(ok_stream("Done.")) == "✅ Done."
    assert "".join(error_stream("Failed.")) == "❌ Failed."

def test_exception_stream():
    try:
        raise ValueError("Something went wrong")
    except ValueError as e:
        ex = e

    stream = exception_stream(ex)
    res = "".join(stream)
    assert res.startswith("❌ `Something went wrong`\n\n<details>\n<summary>Stack trace</summary>")
    assert "ValueError: Something went wrong" in res
    assert "```" in res # check for code block
    assert "</details>" in res

def test_exception_stream_no_message():
    try:
        raise ValueError()
    except ValueError as e:
        ex = e

    stream = exception_stream(ex)
    res = "".join(stream)
    assert res.startswith("❌ `ValueError`\n\n<details>\n<summary>Stack trace</summary>")

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
