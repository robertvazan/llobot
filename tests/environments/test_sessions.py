import pytest
from llobot.chats import ChatIntent, ChatMessage
from llobot.environments.sessions import SessionEnv
import llobot.text

def test_session_env_default():
    """Tests the default state of SessionEnv."""
    env = SessionEnv()
    assert not env.recording()
    assert env.content() == ""
    assert env.message() is None

def test_session_env_append_not_recording():
    """Tests that append() is a no-op when not recording."""
    env = SessionEnv()
    env.append("some text")
    assert env.content() == ""

def test_session_env_recording():
    """Tests enabling recording."""
    env = SessionEnv()
    env.record()
    assert env.recording()

def test_session_env_append():
    """Tests appending fragments to the session message."""
    env = SessionEnv()
    env.record()
    env.append("First part.")
    env.append(None)
    env.append("")
    env.append("Second part.")
    expected = llobot.text.concat("First part.", "Second part.")
    assert env.content() == expected

def test_session_env_message():
    """Tests creating a ChatMessage from session content."""
    env = SessionEnv()
    env.record()
    env.append("Session content.")
    message = env.message()
    assert isinstance(message, ChatMessage)
    assert message.intent == ChatIntent.SESSION
    assert message.content == "Session content."

def test_session_env_stream_empty():
    """Tests that stream() returns an empty stream when there is no content."""
    env = SessionEnv()
    stream = env.stream()
    assert list(stream) == []

def test_session_env_stream_with_content():
    """Tests that stream() returns a valid stream for session content."""
    env = SessionEnv()
    env.record()
    env.append("Session stream content.")
    stream = env.stream()
    assert list(stream) == [ChatIntent.SESSION, "Session stream content."]
