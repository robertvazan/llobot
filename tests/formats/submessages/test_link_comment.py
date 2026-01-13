from __future__ import annotations
import re
import pytest
from textwrap import dedent
from llobot.chats.thread import ChatThread
from llobot.chats.message import ChatMessage
from llobot.chats.intent import ChatIntent
from llobot.chats.stream import record_stream
from llobot.formats.submessages.link_comment import LinkCommentSubmessageFormat

formatter = LinkCommentSubmessageFormat()

CASES = [
    (
        ChatThread([
            ChatMessage(ChatIntent.RESPONSE, "Response content.")
        ]),
        """
        Response content.
        """
    ),
    (
        ChatThread([
            ChatMessage(ChatIntent.RESPONSE, "Response content."),
            ChatMessage(ChatIntent.SYSTEM, "System info.")
        ]),
        """
        Response content.

        [//]: # (System)

        <details>
        <summary>System</summary>

        System info.

        </details>
        """
    ),
    (
        ChatThread([
            ChatMessage(ChatIntent.STATUS, "Status update."),
            ChatMessage(ChatIntent.RESPONSE, "Response content.")
        ]),
        """
        [//]: # (Status)

        Status update.

        [//]: # (Response)

        Response content.
        """
    ),
    (
        ChatThread([
            ChatMessage(ChatIntent.PROMPT, "User prompt 1."),
            ChatMessage(ChatIntent.RESPONSE, "Response 1."),
            ChatMessage(ChatIntent.PROMPT, "User prompt 2."),
            ChatMessage(ChatIntent.RESPONSE, "Response 2.")
        ]),
        """
        [//]: # (Prompt)

        <details>
        <summary>Prompt</summary>

        User prompt 1.

        </details>

        [//]: # (Response)

        Response 1.

        [//]: # (Prompt)

        <details>
        <summary>Prompt</summary>

        User prompt 2.

        </details>

        [//]: # (Response)

        Response 2.
        """
    ),
    (
        ChatThread([
            ChatMessage(ChatIntent.RESPONSE, "[//]: # (System)\nNormal content"),
            ChatMessage(ChatIntent.PROMPT, "[//]: # (Escaped-System)"),
        ]),
        """
        [//]: # (Escaped-System)
        Normal content

        [//]: # (Prompt)

        <details>
        <summary>Prompt</summary>

        [//]: # (Escaped-Escaped-System)

        </details>
        """
    )
]

# Helper to dedent and strip expected string
def normalize_expected(s: str) -> str:
    return dedent(s).strip()

@pytest.mark.parametrize("chat,expected", CASES)
def test_render_consistency(chat: ChatThread, expected: str):
    """Test that render and render_stream produce identical output."""
    rendered_str = formatter.render(chat)

    stream_result = record_stream(formatter.render_stream(chat.stream()))
    assert len(stream_result) == 1
    assert stream_result[0].intent == ChatIntent.RESPONSE
    stream_str = stream_result[0].content

    assert rendered_str == stream_str

@pytest.mark.parametrize("chat,expected", CASES)
def test_roundtrip(chat: ChatThread, expected: str):
    """Test roundtrip for both rendering methods."""
    # Render -> Parse
    rendered = formatter.render(chat)
    parsed = formatter.parse(rendered)
    assert parsed == chat

    # Render Stream -> Parse
    stream_result = record_stream(formatter.render_stream(chat.stream()))
    parsed_stream = formatter.parse(stream_result[0].content)
    assert parsed_stream == chat

@pytest.mark.parametrize("chat,expected", CASES)
def test_parse_chat_roundtrip(chat: ChatThread, expected: str):
    """Test roundtrip via parse_chat."""
    rendered = formatter.render(chat)
    container_chat = ChatThread([ChatMessage(ChatIntent.RESPONSE, rendered)])
    restored = formatter.parse_chat(container_chat)
    assert restored == chat

@pytest.mark.parametrize("chat,expected", CASES)
def test_output_format(chat: ChatThread, expected: str):
    """Test output format matches expected string."""
    rendered = formatter.render(chat)
    assert rendered == normalize_expected(expected)

def test_parse_raises_on_invalid_intent():
    """Test that parse allows ChatIntent.parse to raise ValueError on invalid intent."""
    text = "[//]: # (InvalidIntent)\nContent"
    with pytest.raises(ValueError, match="Unknown intent: InvalidIntent"):
        formatter.parse(text)

def test_implicit_empty_response():
    """Test that implicit empty response is parsed correctly."""
    chat = ChatThread([
        ChatMessage(ChatIntent.RESPONSE, ""),
        ChatMessage(ChatIntent.SYSTEM, "Sys")
    ])
    # Render should produce empty string followed by separator and system message
    rendered = formatter.render(chat)
    # Expect: "\n\n[//]: # (System)\n\n<details>\n<summary>System</summary>\n\nSys\n\n</details>"
    assert rendered.startswith("\n\n")
    parsed = formatter.parse(rendered)
    assert parsed == chat

def test_system_start_no_implicit_response():
    """Test that a chat starting with SYSTEM does not create an empty default response."""
    chat = ChatThread([
        ChatMessage(ChatIntent.SYSTEM, "Sys"),
        ChatMessage(ChatIntent.RESPONSE, "Resp")
    ])
    rendered = formatter.render(chat)
    assert rendered.strip().startswith("[//]: # (System)")
    parsed = formatter.parse(rendered)
    assert parsed == chat

def test_render_stream_buffers_status():
    """Test that STATUS messages are buffered and yielded as a single chunk."""
    # Input stream with a fragmented status message
    stream = [
        ChatIntent.STATUS,
        "Status ",
        "update ",
        "in ",
        "chunks.",
        ChatIntent.RESPONSE,
        "Response ",
        "stream."
    ]

    result = list(formatter.render_stream(stream))

    # Filter strings to check chunking
    result_strings = [x for x in result if isinstance(x, str) and x]

    status_body = "Status update in chunks."

    # Verify the full body exists as a single token
    assert status_body in result_strings, "Status body should be present as a single string"

    # Verify original chunks are NOT present individually
    assert "Status " not in result_strings
    assert "update " not in result_strings
    assert "in " not in result_strings
    assert "chunks." not in result_strings

def test_render_stream_does_not_buffer_response():
    """Test that RESPONSE messages are NOT buffered."""
    stream = [
        ChatIntent.RESPONSE,
        "Chunk 1",
        "Chunk 2"
    ]

    result = list(formatter.render_stream(stream))
    strings = [x for x in result if isinstance(x, str)]

    assert "Chunk 1" in strings
    assert "Chunk 2" in strings
    assert "Chunk 1Chunk 2" not in strings

def test_render_stream_buffers_status_with_newlines():
    """Test buffering of STATUS messages containing newlines."""
    stream = [
        ChatIntent.STATUS,
        "Line 1\n",
        "Line 2"
    ]

    result = list(formatter.render_stream(stream))
    strings = [x for x in result if isinstance(x, str)]

    expected_body = "Line 1\nLine 2"

    assert expected_body in strings
