import pytest
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.environments import Environment
from llobot.environments.session import SessionEnv
from llobot.utils.text import concat_documents

def test_session_message_env_default():
    """Tests the default state of SessionEnv."""
    env = SessionEnv()
    assert env.content() == ""
    assert env.message() is None
    assert not env.populated

def test_session_message_env_append():
    """Tests appending fragments to the session message."""
    env = SessionEnv()
    env.append("First part.")
    env.append(None)
    env.append("")
    env.append("Second part.")
    expected = concat_documents("First part.", "Second part.")
    assert env.content() == expected
    assert env.populated

def test_session_message_env_message():
    """Tests creating a ChatMessage from session content."""
    env = SessionEnv()
    env.append("Session content.")
    message = env.message()
    assert isinstance(message, ChatMessage)
    assert message.intent == ChatIntent.SESSION
    assert message.content == "Session content."
    assert env.populated

def test_session_message_env_stream_empty():
    """Tests that stream() returns an empty stream when there is no content."""
    env = SessionEnv()
    stream = env.stream()
    assert list(stream) == []
    assert not env.populated

def test_session_message_env_stream_with_content():
    """Tests that stream() returns a valid stream for session content."""
    env = SessionEnv()
    env.append("Session stream content.")
    stream = env.stream()
    assert list(stream) == [ChatIntent.SESSION, "Session stream content."]
    assert env.populated
