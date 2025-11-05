from __future__ import annotations
from textwrap import dedent
from unittest.mock import patch
from llobot.chats.thread import ChatThread
from llobot.chats.message import ChatMessage
from llobot.chats.intent import ChatIntent
from llobot.chats.stream import record_stream
from llobot.formats.submessages.link_comment import LinkCommentSubmessageFormat

formatter = LinkCommentSubmessageFormat()
MOCK_IDS = ['id1', 'id2', 'id3', 'id4', 'id5', 'id6']

def test_render_empty():
    chat = ChatThread()
    content = formatter.render(chat)
    assert content == ""

@patch('llobot.formats.submessages.link_comment._new_id', side_effect=MOCK_IDS)
def test_render_single_message(_):
    chat = ChatThread([
        ChatMessage(ChatIntent.SYSTEM, "System prompt content.")
    ])
    content = formatter.render(chat)
    expected = dedent("""
        <details>
        <summary>System</summary>

        [//]: # (System: id1)

        System prompt content.

        [//]: # (id1)

        </details>
    """).strip()
    assert content == expected

@patch('llobot.formats.submessages.link_comment._new_id', side_effect=MOCK_IDS)
def test_render_multiple_messages(_):
    chat = ChatThread([
        ChatMessage(ChatIntent.SYSTEM, "System prompt content."),
        ChatMessage(ChatIntent.AFFIRMATION, "Okay"),
        ChatMessage(ChatIntent.PROMPT, "User prompt.")
    ])
    content = formatter.render(chat)
    expected = dedent("""
        <details>
        <summary>System</summary>

        [//]: # (System: id1)

        System prompt content.

        [//]: # (id1)

        </details>

        <details>
        <summary>Affirmation</summary>

        [//]: # (Affirmation: id2)

        Okay

        [//]: # (id2)

        </details>

        <details>
        <summary>Prompt</summary>

        [//]: # (Prompt: id3)

        User prompt.

        [//]: # (id3)

        </details>
    """).strip()
    assert content == expected

@patch('llobot.formats.submessages.link_comment._new_id', side_effect=MOCK_IDS)
def test_render_with_response_and_status(_):
    chat = ChatThread([
        ChatMessage(ChatIntent.RESPONSE, "This is a response."),
        ChatMessage(ChatIntent.SYSTEM, "System prompt content."),
        ChatMessage(ChatIntent.STATUS, "This is a status message."),
        ChatMessage(ChatIntent.RESPONSE, "Another response.")
    ])
    content = formatter.render(chat)
    expected = dedent("""
        [//]: # (Response: id1)

        This is a response.

        [//]: # (id1)

        <details>
        <summary>System</summary>

        [//]: # (System: id2)

        System prompt content.

        [//]: # (id2)

        </details>

        [//]: # (Status: id3)

        This is a status message.

        [//]: # (id3)

        [//]: # (Response: id4)

        Another response.

        [//]: # (id4)
    """).strip()
    assert content == expected

def test_parse_empty():
    chat = formatter.parse("")
    assert not chat

def test_parse_single_message():
    text = dedent("""
        <details>
        <summary>System</summary>

        [//]: # (System: id1)

        System prompt content.

        [//]: # (id1)

        </details>
    """).strip()
    chat = formatter.parse(text)
    assert len(chat) == 1
    assert chat[0] == ChatMessage(ChatIntent.SYSTEM, "System prompt content.")

def test_parse_multiple_messages():
    text = dedent("""
        <details>
        <summary>System</summary>
        [//]: # (System: id1)
        System prompt content.
        [//]: # (id1)
        </details>

        [//]: # (Affirmation: id2)

        Okay

        [//]: # (id2)
        <details>
        <summary>Prompt</summary>
        [//]: # (Prompt: id3)
        User prompt.
        [//]: # (id3)
        </details>
    """).strip()
    chat = formatter.parse(text)
    expected = ChatThread([
        ChatMessage(ChatIntent.SYSTEM, "System prompt content."),
        ChatMessage(ChatIntent.AFFIRMATION, "Okay"),
        ChatMessage(ChatIntent.PROMPT, "User prompt.")
    ])
    assert chat == expected

def test_parse_with_response_and_junk():
    text = dedent("""
        Some leading junk.
        [//]: # (Response: id1)

        This is a response.

        [//]: # (id1)
        Some junk in between.
        <details>
        <summary>System</summary>

        [//]: # (System: id2)

        System prompt content.

        [//]: # (id2)

        </details>
        Trailing junk.
    """).strip()
    chat = formatter.parse(text)
    expected = ChatThread([
        ChatMessage(ChatIntent.RESPONSE, "This is a response."),
        ChatMessage(ChatIntent.SYSTEM, "System prompt content."),
    ])
    assert chat == expected

def test_parse_with_newlines():
    text = dedent("""
        [//]: # (System: id1)

        Line 1
        Line 2

        Line 4

        [//]: # (id1)
    """).strip()
    chat = formatter.parse(text)
    expected_content = "Line 1\nLine 2\n\nLine 4"
    assert len(chat) == 1
    assert chat[0] == ChatMessage(ChatIntent.SYSTEM, expected_content)

def test_parse_empty_content():
    text = dedent("""
        [//]: # (System: id1)

        [//]: # (id1)
    """).strip()
    chat = formatter.parse(text)
    assert len(chat) == 1
    assert chat[0] == ChatMessage(ChatIntent.SYSTEM, "")

def test_parse_malformed_submessage_no_closer():
    text = dedent("""
        [//]: # (System: id1)
        System content.
        ... missing closing comment
    """).strip()
    chat = formatter.parse(text)
    assert not chat

def test_parse_malformed_intent():
    text = dedent("""
        [//]: # (BogusIntent: id1)
        System content.
        [//]: # (id1)
    """).strip()
    chat = formatter.parse(text)
    assert not chat

@patch('llobot.formats.submessages.link_comment._new_id', side_effect=MOCK_IDS)
def test_roundtrip(_):
    chat = ChatThread([
        ChatMessage(ChatIntent.RESPONSE, "Response message."),
        ChatMessage(ChatIntent.SYSTEM, "System prompt content."),
        ChatMessage(ChatIntent.AFFIRMATION, "Okay"),
        ChatMessage(ChatIntent.PROMPT, "User prompt with\nnewlines and\n\nstuff."),
        ChatMessage(ChatIntent.STATUS, "Status message."),
        ChatMessage(ChatIntent.RESPONSE, "Another response.")
    ])
    rendered = formatter.render(chat)
    parsed = formatter.parse(rendered)
    # Don't compare directly as IDs will be different
    assert len(parsed) == len(chat)
    for p, c in zip(parsed, chat):
        assert p.intent == c.intent
        assert p.content == c.content

@patch('llobot.formats.submessages.link_comment._new_id', side_effect=MOCK_IDS)
def test_roundtrip_empty_content(_):
    chat = ChatThread([
        ChatMessage(ChatIntent.SYSTEM, "System prompt content."),
        ChatMessage(ChatIntent.AFFIRMATION, ""),
        ChatMessage(ChatIntent.PROMPT, "User prompt.")
    ])
    rendered = formatter.render(chat)
    parsed = formatter.parse(rendered)
    assert len(parsed) == len(chat)
    for p, c in zip(parsed, chat):
        assert p.intent == c.intent
        assert p.content == c.content

@patch('llobot.formats.submessages.link_comment._new_id', side_effect=MOCK_IDS)
def test_render_stream_empty(_):
    stream = []
    rendered_chat = record_stream(formatter.render_stream(stream))
    assert not rendered_chat[0].content

@patch('llobot.formats.submessages.link_comment._new_id', side_effect=MOCK_IDS)
def test_render_stream_single_response_message(_):
    stream = iter([ChatIntent.RESPONSE, "Hello world."])
    rendered_chat = record_stream(formatter.render_stream(stream))
    assert len(rendered_chat) == 1
    assert rendered_chat[0].intent == ChatIntent.RESPONSE
    result = rendered_chat[0].content
    expected = dedent("""
        [//]: # (Response: id1)

        Hello world.

        [//]: # (id1)
    """).strip()
    assert result == expected

@patch('llobot.formats.submessages.link_comment._new_id', side_effect=MOCK_IDS)
def test_render_stream_single_status_message(_):
    stream = iter([ChatIntent.STATUS, "Status message."])
    rendered_chat = record_stream(formatter.render_stream(stream))
    assert len(rendered_chat) == 1
    assert rendered_chat[0].intent == ChatIntent.RESPONSE
    result = rendered_chat[0].content
    expected = dedent("""
        [//]: # (Status: id1)

        Status message.

        [//]: # (id1)
    """).strip()
    assert result == expected

@patch('llobot.formats.submessages.link_comment._new_id', side_effect=MOCK_IDS)
def test_render_stream_single_other_message(_):
    stream = [ChatIntent.SYSTEM, "System message."]
    rendered_chat = record_stream(formatter.render_stream(stream))
    assert len(rendered_chat) == 1
    assert rendered_chat[0].intent == ChatIntent.RESPONSE
    result = rendered_chat[0].content
    expected = dedent("""
        <details>
        <summary>System</summary>

        [//]: # (System: id1)

        System message.

        [//]: # (id1)

        </details>
    """).strip()
    assert result == expected

@patch('llobot.formats.submessages.link_comment._new_id', side_effect=MOCK_IDS)
def test_render_stream_empty_message(_):
    stream = [ChatIntent.SYSTEM, ChatIntent.PROMPT, "Content"]
    rendered_chat = record_stream(formatter.render_stream(stream))
    assert len(rendered_chat) == 1
    result = rendered_chat[0].content
    expected = dedent("""
        <details>
        <summary>System</summary>

        [//]: # (System: id1)

        [//]: # (id1)

        </details>

        <details>
        <summary>Prompt</summary>

        [//]: # (Prompt: id2)

        Content

        [//]: # (id2)

        </details>
    """).strip()
    assert result == expected

@patch('llobot.formats.submessages.link_comment._new_id', side_effect=MOCK_IDS)
def test_render_stream_multiple_messages(_):
    stream = [
        ChatIntent.RESPONSE, "Response part 1.", " Response part 2.",
        ChatIntent.SYSTEM, "System message.",
        ChatIntent.STATUS, "Status message.",
        ChatIntent.PROMPT, "Prompt message."
    ]
    rendered_chat = record_stream(formatter.render_stream(stream))
    assert len(rendered_chat) == 1
    assert rendered_chat[0].intent == ChatIntent.RESPONSE
    result = rendered_chat[0].content
    expected = dedent("""
        [//]: # (Response: id1)

        Response part 1. Response part 2.

        [//]: # (id1)

        <details>
        <summary>System</summary>

        [//]: # (System: id2)

        System message.

        [//]: # (id2)

        </details>

        [//]: # (Status: id3)

        Status message.

        [//]: # (id3)

        <details>
        <summary>Prompt</summary>

        [//]: # (Prompt: id4)

        Prompt message.

        [//]: # (id4)

        </details>
    """).strip()
    assert result == expected

def test_parse_chat_empty():
    chat = ChatThread()
    parsed = formatter.parse_chat(chat)
    assert parsed == chat

def test_parse_chat_no_response():
    chat = ChatThread([
        ChatMessage(ChatIntent.SYSTEM, "System message."),
        ChatMessage(ChatIntent.PROMPT, "User prompt.")
    ])
    parsed = formatter.parse_chat(chat)
    assert parsed == chat

def test_parse_chat_with_submessages():
    response_content = dedent("""
        This is a response.

        [//]: # (System: id1)

        System prompt content.

        [//]: # (id1)

        Another response part.
    """).strip()
    chat = ChatThread([
        ChatMessage(ChatIntent.PROMPT, "User prompt."),
        ChatMessage(ChatIntent.RESPONSE, response_content)
    ])
    parsed = formatter.parse_chat(chat)
    expected = ChatThread([
        ChatMessage(ChatIntent.PROMPT, "User prompt."),
        ChatMessage(ChatIntent.SYSTEM, "System prompt content."),
    ])
    assert parsed == expected
