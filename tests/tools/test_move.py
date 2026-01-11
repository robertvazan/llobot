from pathlib import Path, PurePosixPath
import pytest
from llobot.chats.intent import ChatIntent
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.projects import ProjectEnv
from llobot.projects.directory import DirectoryProject
from llobot.projects.library.predefined import PredefinedProjectLibrary
from llobot.tools.move import MoveTool, MoveToolCall

@pytest.fixture
def project(tmp_path: Path) -> DirectoryProject:
    proj_dir = tmp_path / "myproject"
    proj_dir.mkdir()
    (proj_dir / "a.txt").write_text("content")
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

def test_move_tool_matches_and_parses_line(env: Environment):
    tool = MoveTool()
    line = "mv ~/myproject/a.txt ~/myproject/b.txt"

    assert tool.matches_line(env, line)

    call = tool.parse_line(env, line)
    assert isinstance(call, MoveToolCall)
    assert call._source == "~/myproject/a.txt"
    assert call._destination == "~/myproject/b.txt"

def test_move_tool_quoted_paths(env: Environment):
    tool = MoveTool()
    line = "mv \"~/myproject/foo bar.txt\" '~/myproject/baz qux.txt'"

    assert tool.matches_line(env, line)

    call = tool.parse_line(env, line)
    assert isinstance(call, MoveToolCall)
    assert call._source == "~/myproject/foo bar.txt"
    assert call._destination == "~/myproject/baz qux.txt"

def test_move_tool_backslash_escape_space(env: Environment):
    tool = MoveTool()
    line = r"mv ~/myproject/foo\ bar.txt ~/myproject/baz\ qux.txt"

    assert tool.matches_line(env, line)

    call = tool.parse_line(env, line)
    assert isinstance(call, MoveToolCall)
    assert call._source == "~/myproject/foo bar.txt"
    assert call._destination == "~/myproject/baz qux.txt"

def test_move_tool_execute(env: Environment):
    call = MoveToolCall("~/myproject/a.txt", "~/myproject/b.txt")
    call.execute(env)

    project = env[ProjectEnv].union
    assert project.read(PurePosixPath("myproject/a.txt")) is None
    assert project.read(PurePosixPath("myproject/b.txt")) == "content\n"

def test_move_tool_overwrite(env: Environment):
    project = env[ProjectEnv].union
    project.write(PurePosixPath("myproject/b.txt"), "old content")
    call = MoveToolCall("~/myproject/a.txt", "~/myproject/b.txt")
    call.execute(env)
    log = "\n".join(m.content for m in env[ContextEnv].build().messages if m.intent == ChatIntent.STATUS)
    assert "Moved ~/myproject/a.txt to ~/myproject/b.txt (overwriting ~/myproject/b.txt)" in log
    assert project.read(PurePosixPath("myproject/b.txt")) == "content\n"

def test_move_tool_no_match(env: Environment):
    tool = MoveTool()
    assert not tool.matches_line(env, "cp a b")
    assert not tool.matches_line(env, "mv a b c")

def test_move_tool_missing_tilde(env: Environment):
    tool = MoveTool()
    line = "mv myproject/a.txt ~/myproject/b.txt"
    # matches_line should return True because it just checks shlex parts
    assert tool.matches_line(env, line)

    call = tool.parse_line(env, line)
    with pytest.raises(ValueError, match="Path must start with ~/"):
        call.execute(env)
