from __future__ import annotations
from textwrap import dedent
from llobot.chats import ChatBranch, ChatMessage, ChatIntent
from llobot.formatters.submessages import standard as standard_formatter
from llobot.models.streams import text as stream_text

def test_format_empty():
    formatter = standard_formatter()
    chat = ChatBranch()
    content = formatter.format(chat)
    assert content == ""

def test_format_single_message():
    formatter = standard_formatter()
    chat = ChatBranch([
        ChatMessage(ChatIntent.SYSTEM, "System prompt content.")
    ])
    content = formatter.format(chat)
    expected = dedent("""
        <details>
        <summary>Nested message: System</summary>

        System prompt content.

        </details>
    """).strip()
    assert content == expected

def test_format_multiple_messages():
    formatter = standard_formatter()
    chat = ChatBranch([
        ChatMessage(ChatIntent.SYSTEM, "System prompt content."),
        ChatMessage(ChatIntent.AFFIRMATION, "Okay."),
        ChatMessage(ChatIntent.PROMPT, "User prompt.")
    ])
    content = formatter.format(chat)
    expected = dedent("""
        <details>
        <summary>Nested message: System</summary>

        System prompt content.

        </details>

        <details>
        <summary>Nested message: Affirmation</summary>

        Okay.

        </details>

        <details>
        <summary>Nested message: Prompt</summary>

        User prompt.

        </details>
    """).strip()
    assert content == expected

def test_format_with_response():
    formatter = standard_formatter()
    chat = ChatBranch([
        ChatMessage(ChatIntent.RESPONSE, "This is a response."),
        ChatMessage(ChatIntent.SYSTEM, "System prompt content."),
        ChatMessage(ChatIntent.RESPONSE, "Another response.")
    ])
    content = formatter.format(chat)
    expected = dedent("""
        This is a response.

        <details>
        <summary>Nested message: System</summary>

        System prompt content.

        </details>

        Another response.
    """).strip()
    assert content == expected

def test_parse_empty():
    formatter = standard_formatter()
    chat = formatter.parse("")
    assert not chat

def test_parse_single_message():
    formatter = standard_formatter()
    text = dedent("""
        <details>
        <summary>Nested message: System</summary>

        System prompt content.

        </details>
    """).strip()
    chat = formatter.parse(text)
    assert len(chat) == 1
    assert chat[0] == ChatMessage(ChatIntent.SYSTEM, "System prompt content.")

def test_parse_multiple_messages():
    formatter = standard_formatter()
    text = dedent("""
        <details>
        <summary>Nested message: System</summary>

        System prompt content.

        </details>

        <details>
        <summary>Nested message: Affirmation</summary>

        Okay.

        </details>

        <details>
        <summary>Nested message: Prompt</summary>

        User prompt.

        </details>
    """).strip()
    chat = formatter.parse(text)
    expected = ChatBranch([
        ChatMessage(ChatIntent.SYSTEM, "System prompt content."),
        ChatMessage(ChatIntent.AFFIRMATION, "Okay."),
        ChatMessage(ChatIntent.PROMPT, "User prompt.")
    ])
    assert chat == expected

def test_parse_with_response():
    formatter = standard_formatter()
    text = dedent("""
        This is a response.

        <details>
        <summary>Nested message: System</summary>

        System prompt content.

        </details>

        Another response.
    """).strip()
    chat = formatter.parse(text)
    expected = ChatBranch([
        ChatMessage(ChatIntent.RESPONSE, "This is a response."),
        ChatMessage(ChatIntent.SYSTEM, "System prompt content."),
        ChatMessage(ChatIntent.RESPONSE, "Another response.")
    ])
    assert chat == expected

def test_parse_with_newlines():
    formatter = standard_formatter()
    text = dedent("""
        <details>
        <summary>Nested message: System</summary>

        Line 1
        Line 2

        Line 4

        </details>
    """).strip()
    chat = formatter.parse(text)
    expected_content = "Line 1\nLine 2\n\nLine 4"
    assert len(chat) == 1
    assert chat[0] == ChatMessage(ChatIntent.SYSTEM, expected_content)

def test_parse_empty_content():
    formatter = standard_formatter()
    text = dedent("""
        <details>
        <summary>Nested message: System</summary>


        </details>
    """).strip()
    chat = formatter.parse(text)
    assert len(chat) == 1
    assert chat[0] == ChatMessage(ChatIntent.SYSTEM, "")

def test_parse_nested_details_in_submessage():
    formatter = standard_formatter()
    text = dedent("""
        <details>
        <summary>Nested message: System</summary>

        Some content.
        <details>
        <summary>Deeper level</summary>

        Even more content.

        </details>
        More content at top level.

        </details>
    """).strip()
    chat = formatter.parse(text)
    expected_content = dedent("""
        Some content.
        <details>
        <summary>Deeper level</summary>

        Even more content.

        </details>
        More content at top level.
    """).strip()
    expected = ChatBranch([
        ChatMessage(ChatIntent.SYSTEM, expected_content)
    ])
    assert chat == expected

def test_parse_nested_details_in_response():
    formatter = standard_formatter()
    text = dedent("""
        This is a response.
        <details>
        <summary>Nested details</summary>

        Content.

        </details>
        Response continues.
    """).strip()
    chat = formatter.parse(text)
    expected_content = dedent("""
        This is a response.
        <details>
        <summary>Nested details</summary>

        Content.

        </details>
        Response continues.
    """).strip()
    expected = ChatBranch([
        ChatMessage(ChatIntent.RESPONSE, expected_content)
    ])
    assert chat == expected

def test_parse_nested_details_mixed():
    formatter = standard_formatter()
    text = dedent("""
        Response part 1.
        <details>
        <summary>Nested details in response</summary>
        Content.
        </details>

        <details>
        <summary>Nested message: System</summary>

        System content with its own details.
        <details><summary>System's details</summary>System's nested content.</details>

        </details>
        Response part 2.
    """).strip()
    chat = formatter.parse(text)

    response1_content = dedent("""
        Response part 1.
        <details>
        <summary>Nested details in response</summary>
        Content.
        </details>
    """).strip()

    system_content = dedent("""
        System content with its own details.
        <details><summary>System's details</summary>System's nested content.</details>
    """).strip()

    expected = ChatBranch([
        ChatMessage(ChatIntent.RESPONSE, response1_content),
        ChatMessage(ChatIntent.SYSTEM, system_content),
        ChatMessage(ChatIntent.RESPONSE, "Response part 2.")
    ])

    assert chat == expected

def test_parse_submessage_with_code_block():
    formatter = standard_formatter()
    text = dedent("""
        <details>
        <summary>Nested message: System</summary>

        Some content.
        ```html
        <details>
        <summary>This is just text</summary>
        </details>
        ```
        More content.

        </details>
    """).strip()
    chat = formatter.parse(text)
    expected_content = dedent("""
        Some content.
        ```html
        <details>
        <summary>This is just text</summary>
        </details>
        ```
        More content.
    """).strip()
    expected = ChatBranch([
        ChatMessage(ChatIntent.SYSTEM, expected_content)
    ])
    assert chat == expected

def test_parse_submessage_with_quad_backtick_code_block():
    formatter = standard_formatter()
    text = dedent("""
        <details>
        <summary>Nested message: System</summary>

        ````markdown
        ```
        <details>
        <summary>This is just text</summary>
        </details>
        ```
        ````
        More content.

        </details>
    """).strip()
    chat = formatter.parse(text)
    expected_content = dedent("""
        ````markdown
        ```
        <details>
        <summary>This is just text</summary>
        </details>
        ```
        ````
        More content.
    """).strip()
    expected = ChatBranch([
        ChatMessage(ChatIntent.SYSTEM, expected_content)
    ])
    assert chat == expected

def test_parse_response_with_code_block():
    formatter = standard_formatter()
    text = dedent("""
        This is a response.
        ```html
        <details>
        <summary>Nested message: System</summary>
        </details>
        ```
        Response continues.
    """).strip()
    chat = formatter.parse(text)
    expected_content = dedent("""
        This is a response.
        ```html
        <details>
        <summary>Nested message: System</summary>
        </details>
        ```
        Response continues.
    """).strip()
    expected = ChatBranch([
        ChatMessage(ChatIntent.RESPONSE, expected_content)
    ])
    assert chat == expected

def test_parse_unstructured_text_is_response():
    formatter = standard_formatter()
    text = dedent("""
        Some leading junk.
        <details>
        <summary>Nested message: System</summary>

        System prompt content.

        </details>
        Some junk in between.
        <details>
        <summary>Nested message: Prompt</summary>

        User prompt.

        </details>
        Trailing junk.
    """).strip()
    chat = formatter.parse(text)
    expected = ChatBranch([
        ChatMessage(ChatIntent.RESPONSE, "Some leading junk."),
        ChatMessage(ChatIntent.SYSTEM, "System prompt content."),
        ChatMessage(ChatIntent.RESPONSE, "Some junk in between."),
        ChatMessage(ChatIntent.PROMPT, "User prompt."),
        ChatMessage(ChatIntent.RESPONSE, "Trailing junk.")
    ])
    assert chat == expected

def test_parse_consecutive_responses_are_merged():
    formatter = standard_formatter()
    text = "Response 1.\n\nResponse 2."
    chat = formatter.parse(text)
    expected = ChatBranch([
        ChatMessage(ChatIntent.RESPONSE, "Response 1.\n\nResponse 2.")
    ])
    assert chat == expected

def test_roundtrip():
    formatter = standard_formatter()
    chat = ChatBranch([
        ChatMessage(ChatIntent.RESPONSE, "Response message."),
        ChatMessage(ChatIntent.SYSTEM, "System prompt content."),
        ChatMessage(ChatIntent.AFFIRMATION, "Okay."),
        ChatMessage(ChatIntent.PROMPT, "User prompt with\nnewlines and\n\nstuff."),
        ChatMessage(ChatIntent.RESPONSE, "Another response.")
    ])
    formatted = formatter.format(chat)
    parsed = formatter.parse(formatted)
    assert parsed == chat

def test_roundtrip_empty_content():
    formatter = standard_formatter()
    chat = ChatBranch([
        ChatMessage(ChatIntent.SYSTEM, "System prompt content."),
        ChatMessage(ChatIntent.AFFIRMATION, ""),
        ChatMessage(ChatIntent.PROMPT, "User prompt.")
    ])
    formatted = formatter.format(chat)
    parsed = formatter.parse(formatted)
    assert parsed == chat

def test_format_stream_empty():
    formatter = standard_formatter()
    stream = []
    result = "".join(formatter.format_stream(stream))
    assert result == ""

def test_format_stream_single_message_strings_only():
    formatter = standard_formatter()
    stream = stream_text("Hello world.")
    result = "".join(formatter.format_stream(stream))
    assert result == "Hello world."

def test_format_stream_single_message_with_intent():
    formatter = standard_formatter()
    stream = [ChatIntent.SYSTEM, "System message."]
    result = "".join(formatter.format_stream(stream))
    expected = dedent("""
        <details>
        <summary>Nested message: System</summary>

        System message.

        </details>
    """).strip()
    assert result == expected

def test_format_stream_multiple_messages():
    formatter = standard_formatter()
    stream = [
        "Response part 1.", " Response part 2.",
        ChatIntent.SYSTEM, "System message.",
        ChatIntent.PROMPT, "Prompt message."
    ]
    result = "".join(formatter.format_stream(stream))
    expected = dedent("""
        Response part 1. Response part 2.

        <details>
        <summary>Nested message: System</summary>

        System message.

        </details>

        <details>
        <summary>Nested message: Prompt</summary>

        Prompt message.

        </details>
    """).strip()
    assert result == expected

def test_format_stream_empty_messages():
    formatter = standard_formatter()
    stream = [
        ChatIntent.SYSTEM,
        "System message.",
        ChatIntent.PROMPT,  # empty prompt
        ChatIntent.RESPONSE,
        "Response here."
    ]
    result = "".join(formatter.format_stream(stream))
    expected = dedent("""
        <details>
        <summary>Nested message: System</summary>

        System message.

        </details>

        <details>
        <summary>Nested message: Prompt</summary>



        </details>

        Response here.
    """).strip()
    assert result == expected

def test_format_stream_ends_with_intent():
    formatter = standard_formatter()
    stream = ["A message.", ChatIntent.SYSTEM]
    result = "".join(formatter.format_stream(stream))
    expected = dedent("""
        A message.

        <details>
        <summary>Nested message: System</summary>



        </details>
    """).strip()
    assert result == expected

def test_parse_chat_empty():
    formatter = standard_formatter()
    chat = ChatBranch()
    parsed = formatter.parse_chat(chat)
    assert parsed == chat

def test_parse_chat_no_response():
    formatter = standard_formatter()
    chat = ChatBranch([
        ChatMessage(ChatIntent.SYSTEM, "System message."),
        ChatMessage(ChatIntent.PROMPT, "User prompt.")
    ])
    parsed = formatter.parse_chat(chat)
    assert parsed == chat

def test_parse_chat_with_submessages():
    formatter = standard_formatter()
    response_content = dedent("""
        This is a response.

        <details>
        <summary>Nested message: System</summary>

        System prompt content.

        </details>

        Another response part.
    """).strip()
    chat = ChatBranch([
        ChatMessage(ChatIntent.PROMPT, "User prompt."),
        ChatMessage(ChatIntent.RESPONSE, response_content)
    ])
    parsed = formatter.parse_chat(chat)
    expected = ChatBranch([
        ChatMessage(ChatIntent.PROMPT, "User prompt."),
        ChatMessage(ChatIntent.RESPONSE, "This is a response."),
        ChatMessage(ChatIntent.SYSTEM, "System prompt content."),
        ChatMessage(ChatIntent.RESPONSE, "Another response part.")
    ])
    assert parsed == expected

def test_parse_chat_multiple_responses():
    formatter = standard_formatter()
    response1_content = dedent("""
        <details>
        <summary>Nested message: Affirmation</summary>

        OK.

        </details>
    """).strip()
    response2_content = "Just a simple response."
    response3_content = dedent("""
        Response part 1.
        <details>
        <summary>Nested message: System</summary>

        System.

        </details>
    """).strip()

    chat = ChatBranch([
        ChatMessage(ChatIntent.PROMPT, "Prompt."),
        ChatMessage(ChatIntent.RESPONSE, response1_content),
        ChatMessage(ChatIntent.RESPONSE, response2_content),
        ChatMessage(ChatIntent.PROMPT, "Another prompt."),
        ChatMessage(ChatIntent.RESPONSE, response3_content),
    ])

    parsed = formatter.parse_chat(chat)

    expected = ChatBranch([
        ChatMessage(ChatIntent.PROMPT, "Prompt."),
        ChatMessage(ChatIntent.AFFIRMATION, "OK."),
        ChatMessage(ChatIntent.RESPONSE, "Just a simple response."),
        ChatMessage(ChatIntent.PROMPT, "Another prompt."),
        ChatMessage(ChatIntent.RESPONSE, "Response part 1."),
        ChatMessage(ChatIntent.SYSTEM, "System."),
    ])
    assert parsed == expected
