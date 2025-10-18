from __future__ import annotations
from textwrap import dedent
from llobot.chats.thread import ChatThread
from llobot.chats.message import ChatMessage
from llobot.chats.intent import ChatIntent
from llobot.formats.submessages.details import DetailsSubmessageFormat
from llobot.models.streams import text_stream

formatter = DetailsSubmessageFormat()

def test_render_empty():
    chat = ChatThread()
    content = formatter.render(chat)
    assert content == ""

def test_render_single_message():
    chat = ChatThread([
        ChatMessage(ChatIntent.SYSTEM, "System prompt content.")
    ])
    content = formatter.render(chat)
    expected = dedent("""
        <details>
        <summary>Nested message: System</summary>

        System prompt content.

        [//]: # (end of nested message)
        </details>
    """).strip()
    assert content == expected

def test_render_multiple_messages():
    chat = ChatThread([
        ChatMessage(ChatIntent.SYSTEM, "System prompt content."),
        ChatMessage(ChatIntent.AFFIRMATION, "Okay"),
        ChatMessage(ChatIntent.PROMPT, "User prompt.")
    ])
    content = formatter.render(chat)
    expected = dedent("""
        <details>
        <summary>Nested message: System</summary>

        System prompt content.

        [//]: # (end of nested message)
        </details>

        <details>
        <summary>Nested message: Affirmation</summary>

        Okay

        [//]: # (end of nested message)
        </details>

        <details>
        <summary>Nested message: Prompt</summary>

        User prompt.

        [//]: # (end of nested message)
        </details>
    """).strip()
    assert content == expected

def test_render_with_response():
    chat = ChatThread([
        ChatMessage(ChatIntent.RESPONSE, "This is a response."),
        ChatMessage(ChatIntent.SYSTEM, "System prompt content."),
        ChatMessage(ChatIntent.RESPONSE, "Another response.")
    ])
    content = formatter.render(chat)
    expected = dedent("""
        This is a response.

        <details>
        <summary>Nested message: System</summary>

        System prompt content.

        [//]: # (end of nested message)
        </details>

        Another response.
    """).strip()
    assert content == expected

def test_parse_empty():
    chat = formatter.parse("")
    assert not chat

def test_parse_single_message():
    text = dedent("""
        <details>
        <summary>Nested message: System</summary>

        System prompt content.

        [//]: # (end of nested message)
        </details>
    """).strip()
    chat = formatter.parse(text)
    assert len(chat) == 1
    assert chat[0] == ChatMessage(ChatIntent.SYSTEM, "System prompt content.")

def test_parse_multiple_messages():
    text = dedent("""
        <details>
        <summary>Nested message: System</summary>

        System prompt content.

        [//]: # (end of nested message)
        </details>

        <details>
        <summary>Nested message: Affirmation</summary>

        Okay

        [//]: # (end of nested message)
        </details>

        <details>
        <summary>Nested message: Prompt</summary>

        User prompt.

        [//]: # (end of nested message)
        </details>
    """).strip()
    chat = formatter.parse(text)
    expected = ChatThread([
        ChatMessage(ChatIntent.SYSTEM, "System prompt content."),
        ChatMessage(ChatIntent.AFFIRMATION, "Okay"),
        ChatMessage(ChatIntent.PROMPT, "User prompt.")
    ])
    assert chat == expected

def test_parse_with_response():
    text = dedent("""
        This is a response.

        <details>
        <summary>Nested message: System</summary>

        System prompt content.

        [//]: # (end of nested message)
        </details>

        Another response.
    """).strip()
    chat = formatter.parse(text)
    expected = ChatThread([
        ChatMessage(ChatIntent.RESPONSE, "This is a response."),
        ChatMessage(ChatIntent.SYSTEM, "System prompt content."),
        ChatMessage(ChatIntent.RESPONSE, "Another response.")
    ])
    assert chat == expected

def test_parse_with_newlines():
    text = dedent("""
        <details>
        <summary>Nested message: System</summary>

        Line 1
        Line 2

        Line 4

        [//]: # (end of nested message)
        </details>
    """).strip()
    chat = formatter.parse(text)
    expected_content = "Line 1\nLine 2\n\nLine 4"
    assert len(chat) == 1
    assert chat[0] == ChatMessage(ChatIntent.SYSTEM, expected_content)

def test_parse_empty_content():
    text = dedent("""
        <details>
        <summary>Nested message: System</summary>


        [//]: # (end of nested message)
        </details>
    """).strip()
    chat = formatter.parse(text)
    assert len(chat) == 1
    assert chat[0] == ChatMessage(ChatIntent.SYSTEM, "")

def test_parse_unstructured_text_is_response():
    text = dedent("""
        Some leading junk.
        <details>
        <summary>Nested message: System</summary>

        System prompt content.

        [//]: # (end of nested message)
        </details>
        Some junk in between.
        <details>
        <summary>Nested message: Prompt</summary>

        User prompt.

        [//]: # (end of nested message)
        </details>
        Trailing junk.
    """).strip()
    chat = formatter.parse(text)
    expected = ChatThread([
        ChatMessage(ChatIntent.RESPONSE, "Some leading junk."),
        ChatMessage(ChatIntent.SYSTEM, "System prompt content."),
        ChatMessage(ChatIntent.RESPONSE, "Some junk in between."),
        ChatMessage(ChatIntent.PROMPT, "User prompt."),
        ChatMessage(ChatIntent.RESPONSE, "Trailing junk.")
    ])
    assert chat == expected

def test_parse_malformed_submessage():
    text = dedent("""
        Response part 1.
        <details>
        <summary>Nested message: System</summary>

        System content.
        ... missing end marker and closing details
    """).strip()
    chat = formatter.parse(text)
    expected = ChatThread([
        ChatMessage(ChatIntent.RESPONSE, 'Response part 1.'),
        ChatMessage(ChatIntent.SYSTEM, 'System content.\n... missing end marker and closing details')
    ])
    assert chat == expected

def test_parse_malformed_summary():
    text = dedent("""
        Response part 1.
        <details>
        <summary>Not a nested message</summary>

        System content.

        [//]: # (end of nested message)
        </details>
    """).strip()
    chat = formatter.parse(text)
    expected = ChatThread([
        ChatMessage(ChatIntent.RESPONSE, text)
    ])
    assert chat == expected

def test_parse_malformed_intent():
    text = dedent("""
        Response part 1.
        <details>
        <summary>Nested message: BogusIntent</summary>

        System content.

        [//]: # (end of nested message)
        </details>
    """).strip()
    chat = formatter.parse(text)
    expected = ChatThread([
        ChatMessage(ChatIntent.RESPONSE, text)
    ])
    assert chat == expected

def test_roundtrip():
    chat = ChatThread([
        ChatMessage(ChatIntent.RESPONSE, "Response message."),
        ChatMessage(ChatIntent.SYSTEM, "System prompt content."),
        ChatMessage(ChatIntent.AFFIRMATION, "Okay"),
        ChatMessage(ChatIntent.PROMPT, "User prompt with\nnewlines and\n\nstuff."),
        ChatMessage(ChatIntent.RESPONSE, "Another response.")
    ])
    rendered = formatter.render(chat)
    parsed = formatter.parse(rendered)
    assert parsed == chat

def test_roundtrip_empty_content():
    chat = ChatThread([
        ChatMessage(ChatIntent.SYSTEM, "System prompt content."),
        ChatMessage(ChatIntent.AFFIRMATION, ""),
        ChatMessage(ChatIntent.PROMPT, "User prompt.")
    ])
    rendered = formatter.render(chat)
    parsed = formatter.parse(rendered)
    assert parsed == chat

def test_render_stream_empty():
    stream = []
    result = "".join(formatter.render_stream(stream))
    assert result == ""

def test_render_stream_single_message_strings_only():
    stream = text_stream("Hello world.")
    result = "".join(formatter.render_stream(stream))
    assert result == "Hello world."

def test_render_stream_single_message_with_intent():
    stream = [ChatIntent.SYSTEM, "System message."]
    result = "".join(formatter.render_stream(stream))
    expected = dedent("""
        <details>
        <summary>Nested message: System</summary>

        System message.

        [//]: # (end of nested message)
        </details>
    """).strip()
    assert result == expected

def test_render_stream_multiple_messages():
    stream = [
        "Response part 1.", " Response part 2.",
        ChatIntent.SYSTEM, "System message.",
        ChatIntent.PROMPT, "Prompt message."
    ]
    result = "".join(formatter.render_stream(stream))
    expected = dedent("""
        Response part 1. Response part 2.

        <details>
        <summary>Nested message: System</summary>

        System message.

        [//]: # (end of nested message)
        </details>

        <details>
        <summary>Nested message: Prompt</summary>

        Prompt message.

        [//]: # (end of nested message)
        </details>
    """).strip()
    assert result == expected

def test_render_stream_empty_messages():
    stream = [
        ChatIntent.SYSTEM,
        "System message.",
        ChatIntent.PROMPT,  # empty prompt
        ChatIntent.RESPONSE,
        "Response here."
    ]
    result = "".join(formatter.render_stream(stream))
    expected = dedent("""
        <details>
        <summary>Nested message: System</summary>

        System message.

        [//]: # (end of nested message)
        </details>

        <details>
        <summary>Nested message: Prompt</summary>



        [//]: # (end of nested message)
        </details>

        Response here.
    """).strip()
    assert result == expected

def test_render_stream_ends_with_intent():
    stream = ["A message.", ChatIntent.SYSTEM]
    result = "".join(formatter.render_stream(stream))
    expected = dedent("""
        A message.

        <details>
        <summary>Nested message: System</summary>



        [//]: # (end of nested message)
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

        <details>
        <summary>Nested message: System</summary>

        System prompt content.

        [//]: # (end of nested message)
        </details>

        Another response part.
    """).strip()
    chat = ChatThread([
        ChatMessage(ChatIntent.PROMPT, "User prompt."),
        ChatMessage(ChatIntent.RESPONSE, response_content)
    ])
    parsed = formatter.parse_chat(chat)
    expected = ChatThread([
        ChatMessage(ChatIntent.PROMPT, "User prompt."),
        ChatMessage(ChatIntent.RESPONSE, "This is a response."),
        ChatMessage(ChatIntent.SYSTEM, "System prompt content."),
        ChatMessage(ChatIntent.RESPONSE, "Another response part.")
    ])
    assert parsed == expected

def test_parse_chat_multiple_responses():
    response1_content = dedent("""
        <details>
        <summary>Nested message: Affirmation</summary>

        Okay

        [//]: # (end of nested message)
        </details>
    """).strip()
    response2_content = "Just a simple response."
    response3_content = dedent("""
        Response part 1.
        <details>
        <summary>Nested message: System</summary>

        System.

        [//]: # (end of nested message)
        </details>
    """).strip()

    chat = ChatThread([
        ChatMessage(ChatIntent.PROMPT, "Prompt."),
        ChatMessage(ChatIntent.RESPONSE, response1_content),
        ChatMessage(ChatIntent.RESPONSE, response2_content),
        ChatMessage(ChatIntent.PROMPT, "Another prompt."),
        ChatMessage(ChatIntent.RESPONSE, response3_content),
    ])

    parsed = formatter.parse_chat(chat)

    expected = ChatThread([
        ChatMessage(ChatIntent.PROMPT, "Prompt."),
        ChatMessage(ChatIntent.AFFIRMATION, "Okay"),
        ChatMessage(ChatIntent.RESPONSE, "Just a simple response."),
        ChatMessage(ChatIntent.PROMPT, "Another prompt."),
        ChatMessage(ChatIntent.RESPONSE, "Response part 1."),
        ChatMessage(ChatIntent.SYSTEM, "System."),
    ])
    assert parsed == expected
