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
from llobot.tools.script.cat import ScriptCat
from llobot.knowledge.subsets.standard import overviews_subset

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

def test_cat_tool_execute(env: Environment):
    tool = ScriptCat()
    assert tool.execute(env, "cat ~/myproject/a.txt")

    context_env = env[ContextEnv]
    context_messages = context_env.build().messages
    log = "\n".join(m.content for m in context_messages if m.intent == ChatIntent.STATUS)
    output = "\n".join(m.content for m in context_messages if m.intent == ChatIntent.SYSTEM)

    assert "Reading also related `~/myproject/README.md`..." in output
    assert "File: ~/myproject/README.md" in output
    assert "# Readme" in output
    assert "File: ~/myproject/a.txt" in output
    assert "content" in output

def test_cat_tool_execute_nested_overviews(env: Environment):
    tool = ScriptCat()
    assert tool.execute(env, "cat ~/myproject/sub/c.txt")

    context_env = env[ContextEnv]
    context_messages = context_env.build().messages
    output = "\n".join(m.content for m in context_messages if m.intent == ChatIntent.SYSTEM)

    indices = [
        output.find("Reading also related `~/myproject/README.md`..."),
        output.find("Reading also related `~/myproject/sub/__init__.py`..."),
    ]
    assert -1 not in indices
    assert indices == sorted(indices)

def test_cat_tool_execute_deduplication(env: Environment):
    # Pre-populate context with the file content
    listing = standard_document_format().render(PurePosixPath("myproject/a.txt"), "content")
    env[ContextEnv].add(ChatMessage(ChatIntent.SYSTEM, listing))

    tool = ScriptCat()
    assert tool.execute(env, "cat ~/myproject/a.txt")

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

def test_cat_tool_overview_deduplication(env: Environment):
    # Pre-populate context with the overview content
    listing = standard_document_format().render(PurePosixPath("myproject/README.md"), "# Readme")
    env[ContextEnv].add(ChatMessage(ChatIntent.SYSTEM, listing))

    tool = ScriptCat()
    assert tool.execute(env, "cat ~/myproject/a.txt")

    context_env = env[ContextEnv]
    context_messages = context_env.build().messages
    log = "\n".join(m.content for m in context_messages if m.intent == ChatIntent.STATUS)
    output = "\n".join(m.content for m in context_messages if m.intent == ChatIntent.SYSTEM)

    assert "Reading also related `~/myproject/README.md`..." not in log
    assert "Reading also related `~/myproject/README.md`..." not in output

def test_cat_tool_execute_python(env: Environment):
    tool = ScriptCat()
    assert tool.execute(env, "cat ~/myproject/b.py")

    context_env = env[ContextEnv]
    context_messages = context_env.build().messages
    output = "\n".join(m.content for m in context_messages if m.intent == ChatIntent.SYSTEM)

    # ExtensionLanguageMapping maps .py to python
    assert "```python" in output
    assert "print('hello')" in output

def test_cat_tool_missing_file_loads_overviews(env: Environment):
    tool = ScriptCat()
    with pytest.raises(ValueError, match="File not found"):
        tool.execute(env, "cat ~/myproject/nonexistent.txt")

    context_env = env[ContextEnv]
    context_messages = context_env.build().messages
    output = "\n".join(m.content for m in context_messages if m.intent == ChatIntent.SYSTEM)

    assert "Reading also related `~/myproject/README.md`..." in output
    assert "File: ~/myproject/README.md" in output

def test_cat_tool_target_is_overview(env: Environment):
    # If we cat the overview itself, it should appear once
    tool = ScriptCat()
    tool.execute(env, "cat ~/myproject/README.md")

    context_env = env[ContextEnv]
    context_messages = context_env.build().messages
    log = "\n".join(m.content for m in context_messages if m.intent == ChatIntent.STATUS)
    output = "\n".join(m.content for m in context_messages if m.intent == ChatIntent.SYSTEM)

    # Should read it only once
    assert "Reading also related `~/myproject/README.md`..." not in log
    assert "Reading also related `~/myproject/README.md`..." not in output
    assert "File `~/myproject/README.md` is already in the context." not in log
    assert output.count("# Readme") == 1

def test_cat_tool_no_match(env: Environment):
    tool = ScriptCat()
    assert not tool.execute(env, "read a")
    assert not tool.execute(env, "cat a b")
