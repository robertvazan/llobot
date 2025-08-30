import pytest
from llobot.models.streams import ModelStream, text, ok, error, exception

def test_stream_concatenation():
    stream1 = text("First part.")
    stream2 = text("Second part.")
    concatenated = stream1 + stream2
    assert concatenated.response() == "First part.\n\nSecond part."

def test_text_stream():
    stream = text("This is a test.")
    chunks = list(stream)
    assert chunks == ["This is a test."]
    assert stream.response() == "This is a test."

def test_text_stream_empty():
    stream = text("")
    chunks = list(stream)
    assert not chunks
    assert stream.response() == ""

def test_ok_error_streams():
    assert text("Ready.").response() == "Ready."
    assert ok("Done.").response() == "✅ Done."
    assert error("Failed.").response() == "❌ Failed."

def test_exception_stream():
    try:
        raise ValueError("Something went wrong")
    except ValueError as e:
        ex = e

    stream = exception(ex)
    response = stream.response()
    assert response.startswith("❌ `Something went wrong`\n\n<details>\n<summary>Stack trace</summary>")
    assert "ValueError: Something went wrong" in response
    assert "```" in response # check for code block
    assert "</details>" in response

def test_exception_stream_no_message():
    try:
        raise ValueError()
    except ValueError as e:
        ex = e

    stream = exception(ex)
    response = stream.response()
    assert response.startswith("❌ `ValueError`\n\n<details>\n<summary>Stack trace</summary>")
