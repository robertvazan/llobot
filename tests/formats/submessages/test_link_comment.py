from __future__ import annotations
import re
import pytest
from llobot.chats.thread import ChatThread
from llobot.chats.message import ChatMessage
from llobot.chats.intent import ChatIntent
from llobot.chats.stream import record_stream
from llobot.formats.submessages.link_comment import LinkCommentSubmessageFormat

formatter = LinkCommentSubmessageFormat()

CASES = [
    # Single response
    ChatThread([
        ChatMessage(ChatIntent.RESPONSE, "Response content.")
    ]),
    # Session + Response
    ChatThread([
        ChatMessage(ChatIntent.SESSION, "Session info."),
        ChatMessage(ChatIntent.RESPONSE, "Response content.")
    ]),
    # Status + Response
    ChatThread([
        ChatMessage(ChatIntent.STATUS, "Status update."),
        ChatMessage(ChatIntent.RESPONSE, "Response content.")
    ]),
    # Complex sequence
    ChatThread([
        ChatMessage(ChatIntent.PROMPT, "User prompt 1."),
        ChatMessage(ChatIntent.SESSION, "Session info."),
        ChatMessage(ChatIntent.RESPONSE, "Response 1."),
        ChatMessage(ChatIntent.PROMPT, "User prompt 2."),
        ChatMessage(ChatIntent.RESPONSE, "Response 2.")
    ]),
    # Empty content cases
    ChatThread([
        ChatMessage(ChatIntent.SYSTEM, "System."),
        ChatMessage(ChatIntent.AFFIRMATION, ""),
        ChatMessage(ChatIntent.PROMPT, "Prompt.")
    ])
]

def normalize_ids(text: str) -> str:
    """Replaces randomized IDs with placeholders for comparison."""
    # Opening tag: [//]: # (Intent: ID) -> [//]: # (Intent: <ID>)
    text = re.sub(r'(\[//\]: # \()([a-zA-Z0-9_-]+): [a-zA-Z0-9_-]{20}(\))', r'\1\2: <ID>\3', text)
    # Closing tag: [//]: # (ID) -> [//]: # (<ID>)
    text = re.sub(r'(\[//\]: # \()[a-zA-Z0-9_-]{20}(\))', r'\1<ID>\2', text)
    return text

@pytest.mark.parametrize("chat", CASES)
def test_render_consistency(chat: ChatThread):
    """Test that render and render_stream produce identical output (structurally)."""
    rendered_str = formatter.render(chat)

    stream_result = record_stream(formatter.render_stream(chat.stream()))
    assert len(stream_result) == 1
    assert stream_result[0].intent == ChatIntent.RESPONSE
    stream_str = stream_result[0].content

    assert normalize_ids(rendered_str) == normalize_ids(stream_str)

@pytest.mark.parametrize("chat", CASES)
def test_roundtrip(chat: ChatThread):
    """Test roundtrip for both rendering methods."""
    # Render -> Parse
    rendered = formatter.render(chat)
    parsed = formatter.parse(rendered)
    assert parsed == chat

    # Render Stream -> Parse
    stream_result = record_stream(formatter.render_stream(chat.stream()))
    parsed_stream = formatter.parse(stream_result[0].content)
    assert parsed_stream == chat

@pytest.mark.parametrize("chat", CASES)
def test_parse_chat_roundtrip(chat: ChatThread):
    """Test roundtrip via parse_chat."""
    rendered = formatter.render(chat)
    container_chat = ChatThread([ChatMessage(ChatIntent.RESPONSE, rendered)])
    restored = formatter.parse_chat(container_chat)
    assert restored == chat

@pytest.mark.parametrize("chat", CASES)
def test_output_format(chat: ChatThread):
    """Test output format using regexes."""
    rendered = formatter.render(chat)
    remaining = rendered

    for i, message in enumerate(chat):
        intent = re.escape(str(message.intent))
        content = re.escape(message.content)

        pattern = r""
        if i > 0:
            pattern += r"\n\n"

        is_wrapped = message.intent not in [ChatIntent.RESPONSE, ChatIntent.STATUS]

        if is_wrapped:
            pattern += fr"<details>\n<summary>{intent}</summary>\n\n"

        # ID is 20 chars base64url-safe
        id_pattern = r"[a-zA-Z0-9_-]{20}"

        # Open comment
        pattern += fr"\[//\]: # \({intent}: (?P<id_{i}>{id_pattern})\)"

        if message.content:
            pattern += fr"\n\n{content}\n\n"
        else:
            pattern += r"\n\n"

        # Closing comment matching ID
        pattern += fr"\[//\]: # \((?P=id_{i})\)"

        if is_wrapped:
            pattern += r"\n\n</details>"

        match = re.match(pattern, remaining)
        assert match, f"Pattern match failed for message {i} ({message.intent}).\nRemaining: {remaining[:100]!r}"

        remaining = remaining[match.end():]

    assert not remaining, f"Trailing content: {remaining!r}"
