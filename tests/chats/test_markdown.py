import pytest
from pathlib import Path
from llobot.chats.intents import ChatIntent
from llobot.chats.messages import ChatMessage
from llobot.chats.branches import ChatBranch
from llobot.chats.markdown import format_chat_as_markdown, parse_chat_as_markdown, save_chat_as_markdown, load_chat_as_markdown

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

def test_format_parse_roundtrip_empty_chat():
    """Tests that an empty chat can be formatted and parsed back."""
    branch = ChatBranch([])
    formatted = format_chat_as_markdown(branch)
    assert formatted == ""
    parsed = parse_chat_as_markdown(formatted)
    assert parsed == branch

def test_format_parse_roundtrip_whitespace_content():
    """Tests roundtrip with content containing only whitespace."""
    branch = ChatBranch([
        ChatMessage(ChatIntent.PROMPT, "  \n "),
    ])
    formatted = format_chat_as_markdown(branch)
    parsed = parse_chat_as_markdown(formatted)
    assert parsed == branch

def test_save_load_roundtrip(tmp_path: Path):
    """Tests that a chat can be saved to and loaded from a file."""
    branch = ChatBranch([
        ChatMessage(ChatIntent.SYSTEM, "System message"),
        ChatMessage(ChatIntent.PROMPT, "User prompt"),
        ChatMessage(ChatIntent.RESPONSE, "Model response"),
    ])
    file_path = tmp_path / "chat.md"

    save_chat_as_markdown(file_path, branch)
    loaded_branch = load_chat_as_markdown(file_path)

    assert loaded_branch == branch

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

def test_parse_invalid_formats():
    """Tests that parsing invalid markdown formats raises ValueError."""
    # Test for `> Escaped-...` without a preceding message
    with pytest.raises(ValueError):
        parse_chat_as_markdown("> Escaped-Prompt\n\nsome content")

    # Test for content after intent without blank lines
    with pytest.raises(ValueError):
        parse_chat_as_markdown("> Prompt\nHello")

    # Test for content before the next intent without a trailing blank line
    with pytest.raises(ValueError):
        parse_chat_as_markdown("> Prompt\n\nHello\n> Response\n\nHi")
