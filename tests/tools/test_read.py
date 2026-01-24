from pathlib import Path, PurePosixPath
import pytest
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.projects import ProjectEnv
from llobot.formats.documents import standard_document_format
from llobot.projects.directory import DirectoryProject
from llobot.projects.library.predefined import PredefinedProjectLibrary
from llobot.tools.read import ReadTool

@pytest.fixture
def project(tmp_path: Path) -> DirectoryProject:
    proj_dir = tmp_path / "myproject"
    proj_dir.mkdir()
    (proj_dir / "a.txt").write_text("content")
    (proj_dir / "b.py").write_text("print('hello')")
    (proj_dir / "README.md").write_text("# Readme")

    sub_dir = proj_dir / "sub"
    sub_dir.mkdir()
    (sub_dir / "c.txt").write_text("subcontent")
    (sub_dir / "__init__.py").write_text("# Init")

    return DirectoryProject(proj_dir, prefix="myproject", mutable=True)

@pytest.fixture
def library(project: DirectoryProject) -> PredefinedProjectLibrary:
    return PredefinedProjectLibrary({"myproject": project})

@pytest.fixture
def env(library: PredefinedProjectLibrary) -> Environment:
    environment = Environment()
    penv = environment[ProjectEnv]
    penv.configure(library)
    penv.add("myproject")
    return environment

def test_read_tool_execute(env: Environment):
    tool = ReadTool()
    content = """
    ~/myproject/a.txt
    """
    assert tool.execute_fenced(env, "Read", "read", content)

    context_env = env[ContextEnv]
    context_messages = context_env.build().messages
    output = "\n".join(m.content for m in context_messages if m.intent == ChatIntent.SYSTEM)

    assert "Reading also related `~/myproject/README.md`..." in output
    assert "File: ~/myproject/README.md" in output
    assert "# Readme" in output
    assert "File: ~/myproject/a.txt" in output
    assert "content" in output

def test_read_tool_execute_multiple(env: Environment):
    tool = ReadTool()
    content = """
    ~/myproject/a.txt
    ~/myproject/sub/c.txt
    """
    assert tool.execute_fenced(env, "Read", "read", content)

    context_env = env[ContextEnv]
    context_messages = context_env.build().messages
    output = "\n".join(m.content for m in context_messages if m.intent == ChatIntent.SYSTEM)

    assert "File: ~/myproject/a.txt" in output
    assert "File: ~/myproject/sub/c.txt" in output
    # README should be included only once
    assert output.count("File: ~/myproject/README.md") == 1
    # Init should be included
    assert "File: ~/myproject/sub/__init__.py" in output

def test_read_tool_deduplication(env: Environment):
    # Pre-populate context with the file content
    listing = standard_document_format().render(PurePosixPath("myproject/a.txt"), "content")
    env[ContextEnv].add(ChatMessage(ChatIntent.SYSTEM, listing))

    tool = ReadTool()
    content = """
    ~/myproject/a.txt
    """
    assert tool.execute_fenced(env, "Read", "read", content)

    context_env = env[ContextEnv]
    context_messages = context_env.build().messages
    log = "\n".join(m.content for m in context_messages if m.intent == ChatIntent.STATUS)
    # We only care about NEWLY ADDED system messages.
    new_system_messages = [m for m in context_messages[1:] if m.intent == ChatIntent.SYSTEM]
    output = "\n".join(m.content for m in new_system_messages)

    assert "Reading also related `~/myproject/README.md`..." in output
    assert "File `~/myproject/a.txt` is already in the context." in log

    assert "File: ~/myproject/README.md" in output
    assert "content" not in output

def test_read_tool_overview_deduplication(env: Environment):
    # Pre-populate context with the overview content
    listing = standard_document_format().render(PurePosixPath("myproject/README.md"), "# Readme")
    env[ContextEnv].add(ChatMessage(ChatIntent.SYSTEM, listing))

    tool = ReadTool()
    content = """
    ~/myproject/a.txt
    """
    assert tool.execute_fenced(env, "Read", "read", content)

    context_env = env[ContextEnv]
    context_messages = context_env.build().messages
    log = "\n".join(m.content for m in context_messages if m.intent == ChatIntent.STATUS)
    output = "\n".join(m.content for m in context_messages if m.intent == ChatIntent.SYSTEM)

    assert "Reading also related `~/myproject/README.md`..." not in log
    assert "Reading also related `~/myproject/README.md`..." not in output

def test_read_tool_missing_file_raises(env: Environment):
    tool = ReadTool()
    content = """
    ~/myproject/nonexistent.txt
    """
    with pytest.raises(ValueError, match="File not found"):
        tool.execute_fenced(env, "Read", "read", content)

    context_env = env[ContextEnv]
    context_messages = context_env.build().messages
    output = "\n".join(m.content for m in context_messages if m.intent == ChatIntent.SYSTEM)
    # Overviews are read before checking file existence
    assert "Reading also related `~/myproject/README.md`..." in output
    assert "File: ~/myproject/README.md" in output

def test_read_tool_match(env: Environment):
    tool = ReadTool()
    assert tool.match_fenced(env, "Read", "read", "")
    assert not tool.match_fenced(env, "Script", "read", "")

def test_read_tool_no_comments(env: Environment):
    tool = ReadTool()
    content = """
    # This is a comment
    ~/myproject/a.txt
    """
    # Comments are no longer supported and are treated as paths, resulting in ValueError
    with pytest.raises(ValueError, match="Path must start with"):
        tool.execute_fenced(env, "Read", "read", content)
