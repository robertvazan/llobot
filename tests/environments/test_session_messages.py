import pytest
from llobot.chats.intents import ChatIntent
from llobot.chats.messages import ChatMessage
from llobot.environments import Environment
from llobot.environments.session_messages import SessionMessageEnv
from llobot.text import concat_documents

def test_session_message_env_default():
    """Tests the default state of SessionMessageEnv."""
    env = SessionMessageEnv()
    assert env.content() == ""
    assert env.message() is None

def test_session_message_env_append():
    """Tests appending fragments to the session message."""
    env = SessionMessageEnv()
    env.append("First part.")
    env.append(None)
    env.append("")
    env.append("Second part.")
    expected = concat_documents("First part.", "Second part.")
    assert env.content() == expected

def test_session_message_env_message():
    """Tests creating a ChatMessage from session content."""
    env = SessionMessageEnv()
    env.append("Session content.")
    message = env.message()
    assert isinstance(message, ChatMessage)
    assert message.intent == ChatIntent.SESSION
    assert message.content == "Session content."

def test_session_message_env_stream_empty():
    """Tests that stream() returns an empty stream when there is no content."""
    env = SessionMessageEnv()
    stream = env.stream()
    assert list(stream) == []

def test_session_message_env_stream_with_content():
    """Tests that stream() returns a valid stream for session content."""
    env = SessionMessageEnv()
    env.append("Session stream content.")
    stream = env.stream()
    assert list(stream) == [ChatIntent.SESSION, "Session stream content."]
