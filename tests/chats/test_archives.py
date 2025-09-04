from datetime import datetime, timedelta
from pathlib import Path
from llobot.chats.intents import ChatIntent
from llobot.chats.messages import ChatMessage
from llobot.chats.branches import ChatBranch
from llobot.chats.archives import markdown_chat_archive, rename_chat_archive
from llobot.time import current_time, format_time

def create_test_chat(content: str) -> ChatBranch:
    """Helper to create a simple test chat branch."""
    return ChatBranch([ChatMessage(ChatIntent.PROMPT, content)])

def test_add_read(tmp_path: Path):
    """Tests that a chat can be added and read back from the archive."""
    archive = markdown_chat_archive(tmp_path)
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
    archive = markdown_chat_archive(tmp_path)
    now = current_time()
    chat = create_test_chat("Hello")
    archive.add("zone1", now, chat)

    assert archive.contains("zone1", now)
    assert not archive.contains("zone1", now + timedelta(seconds=1))
    assert not archive.contains("zone2", now)

def test_remove(tmp_path: Path):
    """Tests that a chat can be removed from the archive."""
    archive = markdown_chat_archive(tmp_path)
    now = current_time()
    chat = create_test_chat("Hello")
    archive.add("zone1", now, chat)
    assert archive.contains("zone1", now)

    archive.remove("zone1", now)
    assert not archive.contains("zone1", now)

def test_scatter(tmp_path: Path):
    """Tests scattering a chat to multiple zones."""
    archive = markdown_chat_archive(tmp_path)
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
    archive = markdown_chat_archive(tmp_path)
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
    archive = markdown_chat_archive(tmp_path)
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
    archive = markdown_chat_archive(tmp_path)
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
    archive = markdown_chat_archive(tmp_path)
    now = current_time()

    chat1 = create_test_chat("1")
    time1 = now - timedelta(seconds=1)
    archive.add("zone", time1, chat1)

    chat2 = create_test_chat("2")
    time2 = now
    archive.add("zone", time2, chat2)

    assert archive.last("zone", cutoff=time1) == (time1, chat1)
    assert archive.last("zone", cutoff=now - timedelta(seconds=2)) == (None, None)

def test_rename_chat_archive(tmp_path: Path):
    """Tests the rename_chat_archive wrapper."""
    archive = markdown_chat_archive(tmp_path)
    renamed_archive = rename_chat_archive(lambda z: f"prefix-{z}", archive)

    now = current_time()
    chat = create_test_chat("Hello")

    renamed_archive.add("zone", now, chat)

    assert not archive.contains("zone", now)
    assert archive.contains("prefix-zone", now)
    assert renamed_archive.contains("zone", now)

    assert renamed_archive.read("zone", now) == chat

    renamed_archive.remove("zone", now)
    assert not archive.contains("prefix-zone", now)
    assert not renamed_archive.contains("zone", now)
