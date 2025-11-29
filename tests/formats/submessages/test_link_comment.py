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
        [//]: # (Response)

        Response content.
        """
    ),
    (
        ChatThread([
            ChatMessage(ChatIntent.SESSION, "Session info."),
            ChatMessage(ChatIntent.RESPONSE, "Response content.")
        ]),
        """
        [//]: # (Session)

        <details>
        <summary>Session</summary>

        Session info.

        </details>

        [//]: # (Response)

        Response content.
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
            ChatMessage(ChatIntent.SESSION, "Session info."),
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

        [//]: # (Session)

        <details>
        <summary>Session</summary>

        Session info.

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
            ChatMessage(ChatIntent.SYSTEM, "System."),
            ChatMessage(ChatIntent.AFFIRMATION, ""),
            ChatMessage(ChatIntent.PROMPT, "Prompt.")
        ]),
        """
        [//]: # (System)

        <details>
        <summary>System</summary>

        System.

        </details>

        [//]: # (Affirmation)

        <details>
        <summary>Affirmation</summary>



        </details>

        [//]: # (Prompt)

        <details>
        <summary>Prompt</summary>

        Prompt.

        </details>
        """
    ),
    (
        ChatThread([
            ChatMessage(ChatIntent.RESPONSE, "[//]: # (System)\nNormal content"),
            ChatMessage(ChatIntent.PROMPT, "[//]: # (Escaped-System)"),
        ]),
        """
        [//]: # (Response)

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
