import pytest
from llobot.models.streams import (
    ModelStream, completed, status, ok, error, exception,
    notify, silence, handler, chat
)
from llobot.chats import ChatBranch, ChatRole

# A simple stream implementation for testing
class ListStream(ModelStream):
    def __init__(self, items: list[str | Exception]):
        super().__init__()
        self._items = iter(items)

    def _receive(self) -> str | None:
        try:
            item = next(self._items)
            if isinstance(item, Exception):
                raise item
            return item
        except StopIteration:
            return None

def test_stream_concatenation():
    stream1 = completed("First part.")
    stream2 = completed("Second part.")
    concatenated = stream1 + stream2
    assert concatenated.response() == "First part.\n\nSecond part."

def test_completed_stream():
    stream = completed("This is a test.", chunk_size=5)
    chunks = list(stream)
    assert chunks == ["This ", "is a ", "test."]
    assert stream.response() == "This is a test."

def test_status_streams():
    assert status("Ready.").response() == "Ready."
    assert ok("Done.").response() == "✅ Done."
    assert error("Failed.").response() == "❌ Failed."

def test_exception_stream():
    try:
        raise ValueError("Something went wrong")
    except ValueError as e:
        ex = e

    stream = exception(ex)
    response = stream.response()
    assert response.startswith("❌ Something went wrong\n\n<details>\n<summary>Stack trace</summary>")
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
    assert response.startswith("❌ ValueError\n\n<details>\n<summary>Stack trace</summary>")

def test_notify_filter():
    source_stream = completed("response")
    called = False

    def callback(stream):
        nonlocal called
        assert stream.response() == "response"
        called = True

    stream = source_stream | notify(callback)
    assert not called
    assert stream.response() == "response"
    assert called

def test_silence_filter():
    source_stream = completed("some long response")
    stream = source_stream | silence()
    assert stream.response() == ""
    # check that source stream was consumed
    assert source_stream.response() == "some long response"

def test_handler_filter_success():
    source_stream = completed("success")
    stream = source_stream | handler()
    assert stream.response() == "success"

def test_handler_filter_exception():
    source_stream = ListStream(["chunk1", ValueError("test error"), "chunk2"])
    stream = source_stream | handler()
    response = stream.response()
    assert response.startswith("chunk1\n\n❌ test error\n\n<details>\n<summary>Stack trace</summary>")
    assert "ValueError: test error" in response

def test_handler_with_callback():
    callback_called = False
    def my_callback():
        nonlocal callback_called
        callback_called = True

    source_stream = ListStream([ValueError("error")])
    stream = source_stream | handler(callback=my_callback)
    stream.response()
    assert callback_called

def test_chat():
    prompt = ChatRole.USER.message("User prompt")
    stream = completed("Model response")
    result_chat = chat(prompt.branch(), stream)

    assert len(result_chat) == 2
    assert result_chat[0] == prompt
    assert result_chat[1].role == ChatRole.MODEL
    assert result_chat[1].content == "Model response"
