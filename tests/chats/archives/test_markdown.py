from datetime import datetime, timedelta
from pathlib import Path
import pytest
from llobot.chats.intents import ChatIntent
from llobot.chats.messages import ChatMessage
from llobot.chats.branches import ChatBranch
from llobot.chats.archives.markdown import MarkdownChatArchive, format_chat_as_markdown, parse_chat_as_markdown, save_chat_as_markdown, load_chat_as_markdown
from llobot.utils.time import current_time, format_time

def create_test_chat(content: str) -> ChatBranch:
    """Helper to create a simple test chat branch."""
    return ChatBranch([ChatMessage(ChatIntent.PROMPT, content)])

def test_add_read(tmp_path: Path):
    """Tests that a chat can be added and read back from the archive."""
    archive = MarkdownChatArchive(tmp_path)
    now = current_time()
    chat = create_test_chat("Hello")
    archive.add("zone1", now, chat)

    read_chat = archive.read("zone1", now)
    assert read_chat is not None
    assert read_chat == chat

    assert archive.read("zone1", now + timedelta(seconds=1)) is None
    assert archive.read("zone2", now) is None

def test_contains(tmp_path: Path):
    """Tests the contains method to check for chat existence."""
    archive = MarkdownChatArchive(tmp_path)
    now = current_time()
    chat = create_test_chat("Hello")
    archive.add("zone1", now, chat)

    assert archive.contains("zone1", now)
    assert not archive.contains("zone1", now + timedelta(seconds=1))
    assert not archive.contains("zone2", now)

def test_remove(tmp_path: Path):
    """Tests that a chat can be removed from the archive."""
    archive = MarkdownChatArchive(tmp_path)
    now = current_time()
    chat = create_test_chat("Hello")
    archive.add("zone1", now, chat)
    assert archive.contains("zone1", now)

    archive.remove("zone1", now)
    assert not archive.contains("zone1", now)

def test_scatter(tmp_path: Path):
    """Tests scattering a chat to multiple zones."""
    archive = MarkdownChatArchive(tmp_path)
    now = current_time()
    chat = create_test_chat("Scatter")

    archive.scatter(["zone1", "zone2"], now, chat)

    assert archive.read("zone1", now) == chat
    assert archive.read("zone2", now) == chat

    # Check if hardlinks are used (if possible)
    path1 = tmp_path / "zone1" / f"{format_time(now)}.md"
    path2 = tmp_path / "zone2" / f"{format_time(now)}.md"

    assert path1.exists()
    assert path2.exists()
    assert path1.read_text() == path2.read_text()
    if hasattr(path1.stat(), 'st_ino'):
        try:
            assert path1.stat().st_ino == path2.stat().st_ino
        except OSError:
            # Some filesystems (e.g. FAT) do not support inodes.
            # The scatter implementation has a fallback, so this is fine.
            pass

def test_recent(tmp_path: Path):
    """Tests retrieving recent chats in descending order of time."""
    archive = MarkdownChatArchive(tmp_path)
    now = current_time()

    chat1 = create_test_chat("1")
    time1 = now - timedelta(seconds=2)
    archive.add("zone", time1, chat1)

    chat2 = create_test_chat("2")
    time2 = now - timedelta(seconds=1)
    archive.add("zone", time2, chat2)

    chat3 = create_test_chat("3")
    time3 = now
    archive.add("zone", time3, chat3)

    recent_chats = list(archive.recent("zone"))

    assert len(recent_chats) == 3
    assert recent_chats[0] == (time3, chat3)
    assert recent_chats[1] == (time2, chat2)
    assert recent_chats[2] == (time1, chat1)

def test_recent_with_cutoff(tmp_path: Path):
    """Tests retrieving recent chats with a cutoff time."""
    archive = MarkdownChatArchive(tmp_path)
    now = current_time()

    chat1 = create_test_chat("1")
    time1 = now - timedelta(seconds=2)
    archive.add("zone", time1, chat1)

    chat2 = create_test_chat("2")
    time2 = now - timedelta(seconds=1)
    archive.add("zone", time2, chat2)

    recent_chats = list(archive.recent("zone", cutoff=time1))
    assert len(recent_chats) == 1
    assert recent_chats[0] == (time1, chat1)

    recent_chats_2 = list(archive.recent("zone", cutoff=time2))
    assert len(recent_chats_2) == 2
    assert recent_chats_2[0] == (time2, chat2)
    assert recent_chats_2[1] == (time1, chat1)

def test_last(tmp_path: Path):
    """Tests retrieving the last chat from a zone."""
    archive = MarkdownChatArchive(tmp_path)
    now = current_time()

    assert archive.last("zone") == (None, None)

    chat1 = create_test_chat("1")
    time1 = now - timedelta(seconds=1)
    archive.add("zone", time1, chat1)

    chat2 = create_test_chat("2")
    time2 = now
    archive.add("zone", time2, chat2)

    assert archive.last("zone") == (time2, chat2)

def test_last_with_cutoff(tmp_path: Path):
    """Tests retrieving the last chat with a cutoff time."""
    archive = MarkdownChatArchive(tmp_path)
    now = current_time()

    chat1 = create_test_chat("1")
    time1 = now - timedelta(seconds=1)
    archive.add("zone", time1, chat1)

    chat2 = create_test_chat("2")
    time2 = now
    archive.add("zone", time2, chat2)

    assert archive.last("zone", cutoff=time1) == (time1, chat1)
    assert archive.last("zone", cutoff=now - timedelta(seconds=2)) == (None, None)

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
