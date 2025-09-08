from __future__ import annotations
from pathlib import Path
import pytest
from llobot.chats.archives import markdown_chat_archive
from llobot.chats.branches import ChatBranch
from llobot.chats.messages import ChatMessage
from llobot.chats.intents import ChatIntent
from llobot.environments import Environment
from llobot.environments.projects import ProjectEnv
from llobot.memories.examples import ExampleMemory
from llobot.projects.dummy import DummyProject

def test_save_and_recent_with_role_only(tmp_path: Path):
    archive = markdown_chat_archive(tmp_path)
    memory = ExampleMemory('test_role', archive=archive)
    env = Environment()
    chat = ChatBranch([ChatMessage(ChatIntent.PROMPT, "Hello"), ChatMessage(ChatIntent.RESPONSE, "Hi")])

    memory.save(chat, env)

    recent_examples = list(memory.recent(env))
    assert len(recent_examples) == 1
    example = recent_examples[0]
    assert len(example.messages) == 2
    assert example[0].intent == ChatIntent.EXAMPLE_PROMPT
    assert example[0].content == "Hello"
    assert example[1].intent == ChatIntent.EXAMPLE_RESPONSE
    assert example[1].content == "Hi"

def test_save_and_recent_with_project_and_role(tmp_path: Path):
    archive = markdown_chat_archive(tmp_path)
    memory = ExampleMemory('test_role', archive=archive)
    env = Environment()
    env[ProjectEnv].set(DummyProject('test_project'))
    chat = ChatBranch([ChatMessage(ChatIntent.PROMPT, "Question")])

    memory.save(chat, env)

    # Check both zones
    assert (tmp_path / 'test_project-test_role').exists()
    assert (tmp_path / 'test_role').exists()

    recent_examples = list(memory.recent(env))
    # It will read from both zones, which are hardlinked, yielding two identical examples.
    assert len(recent_examples) == 2

    env_no_project = Environment()
    recent_no_project = list(memory.recent(env_no_project))
    assert len(recent_no_project) == 1 # only from test_role zone

def test_save_with_project_only(tmp_path: Path):
    archive = markdown_chat_archive(tmp_path)
    memory = ExampleMemory(archive=archive)
    env = Environment()
    env[ProjectEnv].set(DummyProject('test_project'))
    chat = ChatBranch([ChatMessage(ChatIntent.PROMPT, "Data")])

    memory.save(chat, env)

    recent_examples = list(memory.recent(env))
    assert len(recent_examples) == 1
    assert (tmp_path / 'test_project').exists()

def test_save_no_zone_fails(tmp_path: Path):
    archive = markdown_chat_archive(tmp_path)
    memory = ExampleMemory(archive=archive)
    env = Environment()
    chat = ChatBranch([ChatMessage(ChatIntent.PROMPT, "Empty")])

    with pytest.raises(ValueError, match="Cannot save example without a project or role."):
        memory.save(chat, env)

def test_recent_no_zone_is_empty(tmp_path: Path):
    archive = markdown_chat_archive(tmp_path)
    memory = ExampleMemory(archive=archive)
    env = Environment()

    assert not list(memory.recent(env))

def test_save_replaces_last_example(tmp_path: Path):
    archive = markdown_chat_archive(tmp_path)
    memory = ExampleMemory('test_role', archive=archive)
    env = Environment()

    chat1 = ChatBranch([ChatMessage(ChatIntent.PROMPT, "Prompt1"), ChatMessage(ChatIntent.RESPONSE, "Response1")])
    memory.save(chat1, env)

    chat2 = ChatBranch([ChatMessage(ChatIntent.PROMPT, "Prompt1"), ChatMessage(ChatIntent.RESPONSE, "Response2")])
    memory.save(chat2, env)

    recent_examples = list(memory.recent(env))
    assert len(recent_examples) == 1
    assert recent_examples[0][1].content == "Response2"
