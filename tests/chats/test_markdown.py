from llobot.chats.intents import ChatIntent
from llobot.chats.messages import ChatMessage
from llobot.chats.branches import ChatBranch
from llobot.chats.markdown import format, parse

def test_format_parse_roundtrip_simple():
    """Tests that a simple chat can be formatted and parsed back."""
    branch = ChatBranch([
        ChatMessage(ChatIntent.PROMPT, "Hello"),
        ChatMessage(ChatIntent.RESPONSE, "Hi there"),
    ])
    formatted = format(branch)
    parsed = parse(formatted)
    assert parsed == branch

def test_format_parse_roundtrip_multiline():
    """Tests roundtrip with multiline messages."""
    branch = ChatBranch([
        ChatMessage(ChatIntent.PROMPT, "Line 1\nLine 2"),
        ChatMessage(ChatIntent.RESPONSE, "Answer\n\nWith blank line."),
    ])
    formatted = format(branch)
    parsed = parse(formatted)
    assert parsed == branch

def test_format_parse_roundtrip_empty_message():
    """Tests roundtrip with empty messages."""
    branch = ChatBranch([
        ChatMessage(ChatIntent.PROMPT, ""),
        ChatMessage(ChatIntent.RESPONSE, "Hi"),
    ])
    formatted = format(branch)
    parsed = parse(formatted)
    assert parsed == branch

def test_format_parse_roundtrip_trailing_newline():
    """Tests roundtrip with content ending in a newline."""
    branch = ChatBranch([
        ChatMessage(ChatIntent.PROMPT, "Code:\n```\nfoo\n```\n"),
    ])
    formatted = format(branch)
    parsed = parse(formatted)
    assert parsed == branch

def test_escape_intent_like_lines():
    """Tests that lines resembling intent headers are escaped."""
    branch = ChatBranch([
        ChatMessage(ChatIntent.PROMPT, "A line\n> Prompt\nAnother line"),
    ])
    formatted = format(branch)
    assert "> Escaped-Prompt" in formatted
    parsed = parse(formatted)
    assert parsed == branch

def test_parse_with_leading_content():
    """Tests that parsing tolerates content before the first message."""
    text = "Some metadata\n\n> Prompt\n\nHello"
    branch = parse(text)
    assert len(branch) == 1
    assert branch[0] == ChatMessage(ChatIntent.PROMPT, "Hello")
