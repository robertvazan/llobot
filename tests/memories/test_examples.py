from __future__ import annotations
from pathlib import Path
import pytest
from llobot.chats.archives.markdown import MarkdownChatArchive
from llobot.chats.branches import ChatBranch
from llobot.chats.intents import ChatIntent
from llobot.chats.messages import ChatMessage
from llobot.environments import Environment
from llobot.environments.projects import ProjectEnv
from llobot.memories.examples import ExampleMemory
from llobot.projects.dummy import DummyProject
from llobot.utils.time import parse_time

def test_save_and_recent_with_role_only(tmp_path: Path):
    archive = MarkdownChatArchive(tmp_path)
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
    archive = MarkdownChatArchive(tmp_path)
    memory = ExampleMemory('test_role', archive=archive)
    env = Environment()
    env[ProjectEnv].add(DummyProject('test_project'))
    chat = ChatBranch([ChatMessage(ChatIntent.PROMPT, "Question")])

    memory.save(chat, env)

    # Check both zones
    assert (tmp_path / 'test_role' / 'test_project').exists()
    assert (tmp_path / 'test_role').exists()

    recent_examples = list(memory.recent(env))
    # Duplicates are filtered, so only one example is returned.
    assert len(recent_examples) == 1

    env_no_project = Environment()
    recent_no_project = list(memory.recent(env_no_project))
    assert len(recent_no_project) == 1 # only from test_role zone

def test_zones_with_path_like_project_name(tmp_path: Path):
    archive = MarkdownChatArchive(tmp_path)
    memory = ExampleMemory('test_role', archive=archive)
    env = Environment()
    env[ProjectEnv].add(DummyProject('my/project'))
    chat = ChatBranch([ChatMessage(ChatIntent.PROMPT, "Question")])

    memory.save(chat, env)

    # Check both zones are created
    assert (tmp_path / 'test_role' / 'my' / 'project').exists()
    assert (tmp_path / 'test_role').exists()

    # Check if they have content
    assert len(list(archive.recent(Path('test_role/my/project')))) == 1
    assert len(list(archive.recent(Path('test_role')))) == 1

def test_save_with_project_only(tmp_path: Path):
    archive = MarkdownChatArchive(tmp_path)
    memory = ExampleMemory(archive=archive)
    env = Environment()
    env[ProjectEnv].add(DummyProject('test_project'))
    chat = ChatBranch([ChatMessage(ChatIntent.PROMPT, "Data")])

    memory.save(chat, env)

    recent_examples = list(memory.recent(env))
    assert len(recent_examples) == 1
    assert (tmp_path / 'test_project').exists()

def test_save_no_zone_fails(tmp_path: Path):
    archive = MarkdownChatArchive(tmp_path)
    memory = ExampleMemory(archive=archive)
    env = Environment()
    chat = ChatBranch([ChatMessage(ChatIntent.PROMPT, "Empty")])

    with pytest.raises(ValueError, match="Cannot save example without a project or role."):
        memory.save(chat, env)

def test_recent_no_zone_is_empty(tmp_path: Path):
    archive = MarkdownChatArchive(tmp_path)
    memory = ExampleMemory(archive=archive)
    env = Environment()

    assert not list(memory.recent(env))

def test_save_replaces_last_example(tmp_path: Path):
    archive = MarkdownChatArchive(tmp_path)
    memory = ExampleMemory('test_role', archive=archive)
    env = Environment()

    chat1 = ChatBranch([ChatMessage(ChatIntent.PROMPT, "Prompt1"), ChatMessage(ChatIntent.RESPONSE, "Response1")])
    memory.save(chat1, env)

    chat2 = ChatBranch([ChatMessage(ChatIntent.PROMPT, "Prompt1"), ChatMessage(ChatIntent.RESPONSE, "Response2")])
    memory.save(chat2, env)

    recent_examples = list(memory.recent(env))
    assert len(recent_examples) == 1
    assert recent_examples[0][1].content == "Response2"

def test_recent_merges_examples(tmp_path: Path):
    archive = MarkdownChatArchive(tmp_path)
    memory = ExampleMemory('test_role', archive=archive)
    env = Environment()
    env[ProjectEnv].add(DummyProject('p1'))
    env[ProjectEnv].add(DummyProject('p2'))

    chat_p1 = ChatBranch([ChatMessage(ChatIntent.PROMPT, "p1 prompt")])
    chat_p2 = ChatBranch([ChatMessage(ChatIntent.PROMPT, "p2 prompt")])
    chat_role = ChatBranch([ChatMessage(ChatIntent.PROMPT, "role prompt")])
    chat_both = ChatBranch([ChatMessage(ChatIntent.PROMPT, "both prompt")])

    archive.add(Path('test_role/p1'), parse_time('20240101-120000'), chat_p1)
    archive.add(Path('test_role/p2'), parse_time('20240101-140000'), chat_p2)
    archive.add(Path('test_role'), parse_time('20240101-100000'), chat_role)
    # this will be in two zones, but recent should deduplicate it
    archive.scatter([Path('test_role/p1'), Path('test_role/p2')], parse_time('20240101-130000'), chat_both)

    recent = [c[0].content for c in memory.recent(env)]
    assert recent == [
        "p2 prompt",      # 14:00 from p2
        "both prompt",    # 13:00 from p1/p2 (deduplicated)
        "p1 prompt",      # 12:00 from p1
        "role prompt",    # 10:00 from role-only
    ]
