from __future__ import annotations
from pathlib import Path
import pytest
from llobot.chats.markdown import MarkdownChatHistory
from llobot.chats.thread import ChatThread
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.environments import Environment
from llobot.environments.projects import ProjectEnv
from llobot.memories.examples import ExampleMemory
from llobot.projects.library.zone import ZoneKeyedProjectLibrary
from llobot.projects.zone import ZoneProject
from llobot.utils.time import parse_time

def test_save_and_recent_with_role_only(tmp_path: Path):
    history = MarkdownChatHistory(tmp_path)
    memory = ExampleMemory('test_role', history=history)
    env = Environment()
    chat = ChatThread([ChatMessage(ChatIntent.PROMPT, "Hello"), ChatMessage(ChatIntent.RESPONSE, "Hi")])

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
    history = MarkdownChatHistory(tmp_path)
    memory = ExampleMemory('test_role', history=history)
    env = Environment()
    library = ZoneKeyedProjectLibrary(ZoneProject('test_project'))
    project_env = env[ProjectEnv]
    project_env.configure(library)
    project_env.add('test_project')
    chat = ChatThread([ChatMessage(ChatIntent.PROMPT, "Question")])

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

def test_zones_with_path_like_zone(tmp_path: Path):
    history = MarkdownChatHistory(tmp_path)
    memory = ExampleMemory('test_role', history=history)
    env = Environment()
    library = ZoneKeyedProjectLibrary(ZoneProject('my/project'))
    project_env = env[ProjectEnv]
    project_env.configure(library)
    project_env.add('my/project')
    chat = ChatThread([ChatMessage(ChatIntent.PROMPT, "Question")])

    memory.save(chat, env)

    # Check both zones are created
    assert (tmp_path / 'test_role' / 'my' / 'project').exists()
    assert (tmp_path / 'test_role').exists()

    # Check if they have content
    assert len(list(history.recent(Path('test_role/my/project')))) == 1
    assert len(list(history.recent(Path('test_role')))) == 1

def test_save_with_project_only(tmp_path: Path):
    history = MarkdownChatHistory(tmp_path)
    memory = ExampleMemory(history=history)
    env = Environment()
    library = ZoneKeyedProjectLibrary(ZoneProject('test_project'))
    project_env = env[ProjectEnv]
    project_env.configure(library)
    project_env.add('test_project')
    chat = ChatThread([ChatMessage(ChatIntent.PROMPT, "Data")])

    memory.save(chat, env)

    recent_examples = list(memory.recent(env))
    assert len(recent_examples) == 1
    assert (tmp_path / 'test_project').exists()

def test_save_no_zone_fails(tmp_path: Path):
    history = MarkdownChatHistory(tmp_path)
    memory = ExampleMemory(history=history)
    env = Environment()
    chat = ChatThread([ChatMessage(ChatIntent.PROMPT, "Empty")])

    with pytest.raises(ValueError, match="Cannot save example without a project or role."):
        memory.save(chat, env)

def test_recent_no_zone_is_empty(tmp_path: Path):
    history = MarkdownChatHistory(tmp_path)
    memory = ExampleMemory(history=history)
    env = Environment()

    assert not list(memory.recent(env))

def test_save_replaces_last_example(tmp_path: Path):
    history = MarkdownChatHistory(tmp_path)
    memory = ExampleMemory('test_role', history=history)
    env = Environment()

    chat1 = ChatThread([ChatMessage(ChatIntent.PROMPT, "Prompt1"), ChatMessage(ChatIntent.RESPONSE, "Response1")])
    memory.save(chat1, env)

    chat2 = ChatThread([ChatMessage(ChatIntent.PROMPT, "Prompt1"), ChatMessage(ChatIntent.RESPONSE, "Response2")])
    memory.save(chat2, env)

    recent_examples = list(memory.recent(env))
    assert len(recent_examples) == 1
    assert recent_examples[0][1].content == "Response2"

def test_recent_merges_examples(tmp_path: Path):
    history = MarkdownChatHistory(tmp_path)
    memory = ExampleMemory('test_role', history=history)
    env = Environment()
    library = ZoneKeyedProjectLibrary(ZoneProject('p1'), ZoneProject('p2'))
    project_env = env[ProjectEnv]
    project_env.configure(library)
    project_env.add('p1')
    project_env.add('p2')

    chat_p1 = ChatThread([ChatMessage(ChatIntent.PROMPT, "p1 prompt")])
    chat_p2 = ChatThread([ChatMessage(ChatIntent.PROMPT, "p2 prompt")])
    chat_role = ChatThread([ChatMessage(ChatIntent.PROMPT, "role prompt")])
    chat_both = ChatThread([ChatMessage(ChatIntent.PROMPT, "both prompt")])

    history.add(Path('test_role/p1'), parse_time('20240101-120000'), chat_p1)
    history.add(Path('test_role/p2'), parse_time('20240101-140000'), chat_p2)
    history.add(Path('test_role'), parse_time('20240101-100000'), chat_role)
    # this will be in two zones, but recent should deduplicate it
    history.scatter([Path('test_role/p1'), Path('test_role/p2')], parse_time('20240101-130000'), chat_both)

    recent = [c[0].content for c in memory.recent(env)]
    assert recent == [
        "p2 prompt",      # 14:00 from p2
        "both prompt",    # 13:00 from p1/p2 (deduplicated)
        "p1 prompt",      # 12:00 from p1
        "role prompt",    # 10:00 from role-only
    ]
