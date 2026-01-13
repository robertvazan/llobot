"""
Tests for the echo command.
"""
from __future__ import annotations
from llobot.chats.thread import ChatThread
from llobot.chats.message import ChatMessage
from llobot.chats.intent import ChatIntent
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.prompt import PromptEnv
from llobot.commands.echo import handle_echo_command

def test_handle_echo_command():
    """
    Tests that handle_echo_command correctly echoes the context and swallows the prompt.
    """
    env = Environment()
    env[PromptEnv].set(ChatThread([ChatMessage(ChatIntent.PROMPT, "@echo")]))
    env[ContextEnv].add(ChatMessage(ChatIntent.SYSTEM, "System prompt."))

    assert handle_echo_command("echo", env)

    context = env[ContextEnv].build()
    assert len(context) == 2
    assert context[0].intent == ChatIntent.SYSTEM
    assert context[1].intent == ChatIntent.STATUS
    assert context[1].content == "System prompt."
    assert env[PromptEnv].swallowed

def test_handle_echo_details_command():
    """
    Tests that handle_echo_command correctly echoes details and swallows the prompt.
    """
    env = Environment()
    env[PromptEnv].set(ChatThread([ChatMessage(ChatIntent.PROMPT, "@echo-details")]))
    env[ContextEnv].add(ChatMessage(ChatIntent.SYSTEM, "System prompt."))

    assert handle_echo_command("echo-details", env)

    context = env[ContextEnv].build()
    assert len(context) == 2
    assert context[1].intent == ChatIntent.STATUS
    assert "<details>" in context[1].content
    assert "System prompt." in context[1].content
    assert env[PromptEnv].swallowed

def test_handle_unknown_command():
    """
    Tests that handle_echo_command ignores unknown commands.
    """
    env = Environment()
    assert not handle_echo_command("other", env)
