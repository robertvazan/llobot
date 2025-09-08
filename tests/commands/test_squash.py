from pathlib import Path
import pytest
from llobot.chats.archives import standard_chat_archive
from llobot.chats.intents import ChatIntent
from llobot.chats.messages import ChatMessage
from llobot.commands.squash import SquashCommand
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.knowledge import KnowledgeEnv
from llobot.environments.projects import ProjectEnv
from llobot.environments.replay import ReplayEnv
from llobot.environments.status import StatusEnv
from llobot.formats.documents import standard_document_format
from llobot.knowledge import Knowledge
from llobot.memories.examples import ExampleMemory
from llobot.projects.directory import DirectoryProject

def test_squash_command(tmp_path: Path):
    # Project setup
    project_dir = tmp_path / 'project'
    project_dir.mkdir()
    (project_dir / 'file1.txt').write_text('initial content')
    project = DirectoryProject(project_dir)

    # Archive setup
    archive = standard_chat_archive(tmp_path / 'archive')
    examples = ExampleMemory('test-role', archive=archive)
    command = SquashCommand(examples, standard_document_format())
    env = Environment()

    # Environment setup
    env[ProjectEnv].set(project)
    env[ContextEnv].add(ChatMessage(ChatIntent.PROMPT, "User prompt"))
    env[KnowledgeEnv].set(project.load())
    
    # Modify project
    (project_dir / 'file1.txt').write_text('new content')
    (project_dir / 'file2.txt').write_text('new file')
    
    env[ReplayEnv].start_recording()

    # Handle
    assert command.handle('squash', env)

    # Check status
    status = env[StatusEnv]
    assert status.populated
    assert status.content() == "✅ Changes squashed and saved as an example."

    # Check saved example
    saved_examples = list(examples.recent(env))
    assert len(saved_examples) == 1
    example = saved_examples[0]
    assert len(example.messages) == 2
    assert example[0].intent == ChatIntent.EXAMPLE_PROMPT
    assert example[0].content == "User prompt"
    assert example[1].intent == ChatIntent.EXAMPLE_RESPONSE
    
    response_content = example[1].content
    assert 'File: project/file1.txt' in response_content
    assert 'new content' in response_content
    assert 'File: project/file2.txt' in response_content
    assert 'new file' in response_content
    assert 'Removed:' not in response_content

def test_squash_no_changes(tmp_path: Path):
    project_dir = tmp_path / 'project'
    project_dir.mkdir()
    (project_dir / 'file1.txt').write_text('content')
    project = DirectoryProject(project_dir)

    archive = standard_chat_archive(tmp_path / 'archive')
    examples = ExampleMemory('test-role', archive=archive)
    command = SquashCommand(examples, standard_document_format())
    env = Environment()

    env[ProjectEnv].set(project)
    env[ContextEnv].add(ChatMessage(ChatIntent.PROMPT, "User prompt"))
    env[KnowledgeEnv].set(project.load())

    env[ReplayEnv].start_recording()

    with pytest.raises(ValueError, match="No changes detected"):
        command.handle('squash', env)

def test_squash_replay(tmp_path: Path):
    project_dir = tmp_path / 'project'
    project_dir.mkdir()
    project = DirectoryProject(project_dir)

    archive = standard_chat_archive(tmp_path / 'archive')
    examples = ExampleMemory('test-role', archive=archive)
    command = SquashCommand(examples, standard_document_format())
    env = Environment()
    env[ReplayEnv] # initialize

    env[ProjectEnv].set(project)
    env[ContextEnv].add(ChatMessage(ChatIntent.PROMPT, "User prompt"))
    env[KnowledgeEnv].set(Knowledge())

    assert command.handle('squash', env)
    assert not env[StatusEnv].populated
    assert not list(examples.recent(env))
