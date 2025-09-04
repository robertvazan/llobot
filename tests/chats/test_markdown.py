from llobot.chats.intents import ChatIntent
from llobot.chats.messages import ChatMessage
from llobot.chats.branches import ChatBranch
from llobot.chats.markdown import format_chat_as_markdown, parse_chat_as_markdown

def test_format_parse_roundtrip_simple():
    """Tests that a simple chat can be formatted and parsed back."""
    branch = ChatBranch([
        ChatMessage(ChatIntent.PROMPT, "Hello"),
        ChatMessage(ChatIntent.RESPONSE, "Hi there"),
    ])
    formatted = format_chat_as_markdown(branch)
    parsed = parse_chat_as_markdown(formatted)
    assert parsed == branch

def test_format_parse_roundtrip_multiline():
    """Tests roundtrip with multiline messages."""
    branch = ChatBranch([
        ChatMessage(ChatIntent.PROMPT, "Line 1\nLine 2"),
        ChatMessage(ChatIntent.RESPONSE, "Answer\n\nWith blank line."),
    ])
    formatted = format_chat_as_markdown(branch)
    parsed = parse_chat_as_markdown(formatted)
    assert parsed == branch

def test_format_parse_roundtrip_empty_message():
    """Tests roundtrip with empty messages."""
    branch = ChatBranch([
        ChatMessage(ChatIntent.PROMPT, ""),
        ChatMessage(ChatIntent.RESPONSE, "Hi"),
    ])
    formatted = format_chat_as_markdown(branch)
    parsed = parse_chat_as_markdown(formatted)
    assert parsed == branch

def test_format_parse_roundtrip_trailing_newline():
    """Tests roundtrip with content ending in a newline."""
    branch = ChatBranch([
        ChatMessage(ChatIntent.PROMPT, "Code:\n```\nfoo\n```\n"),
    ])
    formatted = format_chat_as_markdown(branch)
    parsed = parse_chat_as_markdown(formatted)
    assert parsed == branch

def test_escape_intent_like_lines():
    """Tests that lines resembling intent headers are escaped."""
    branch = ChatBranch([
        ChatMessage(ChatIntent.PROMPT, "A line\n> Prompt\nAnother line"),
    ])
    formatted = format_chat_as_markdown(branch)
    assert "> Escaped-Prompt" in formatted
    parsed = parse_chat_as_markdown(formatted)
    assert parsed == branch

def test_parse_with_leading_content():
    """Tests that parsing tolerates content before the first message."""
    text = "Some metadata\n\n> Prompt\n\nHello"
    branch = parse_chat_as_markdown(text)
    assert len(branch) == 1
    assert branch[0] == ChatMessage(ChatIntent.PROMPT, "Hello")
