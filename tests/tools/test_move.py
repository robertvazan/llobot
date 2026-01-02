from pathlib import Path, PurePosixPath
from textwrap import dedent
import pytest
from llobot.environments import Environment
from llobot.environments.projects import ProjectEnv
from llobot.environments.tools import ToolEnv
from llobot.projects.directory import DirectoryProject
from llobot.projects.library.home import HomeProjectLibrary
from llobot.tools.move import MoveTool, MoveToolCall

@pytest.fixture
def home_library(tmp_path: Path) -> HomeProjectLibrary:
    return HomeProjectLibrary(str(tmp_path), mutable=True)

@pytest.fixture
def project(home_library: HomeProjectLibrary, tmp_path: Path) -> DirectoryProject:
    proj_dir = tmp_path / "myproject"
    proj_dir.mkdir()
    (proj_dir / "a.txt").write_text("content")
    projects = home_library.lookup("myproject")
    assert projects and isinstance(projects[0], DirectoryProject)
    return projects[0]

@pytest.fixture
def env(home_library: HomeProjectLibrary, project: DirectoryProject) -> Environment:
    environment = Environment()
    penv = environment[ProjectEnv]
    penv.configure(home_library)
    penv.add("myproject")
    return environment

def test_move_tool_matches_and_parses_line(env: Environment):
    tool = MoveTool()
    line = "mv ~/myproject/a.txt ~/myproject/b.txt"

    assert tool.matches_line(env, line)

    call = tool.parse_line(env, line)
    assert isinstance(call, MoveToolCall)
    assert call._source == PurePosixPath("myproject/a.txt")
    assert call._destination == PurePosixPath("myproject/b.txt")

def test_move_tool_quoted_paths(env: Environment):
    tool = MoveTool()
    line = "mv \"~/myproject/foo bar.txt\" '~/myproject/baz qux.txt'"

    assert tool.matches_line(env, line)

    call = tool.parse_line(env, line)
    assert isinstance(call, MoveToolCall)
    assert call._source == PurePosixPath("myproject/foo bar.txt")
    assert call._destination == PurePosixPath("myproject/baz qux.txt")

def test_move_tool_backslash_escape_space(env: Environment):
    tool = MoveTool()
    line = r"mv ~/myproject/foo\ bar.txt ~/myproject/baz\ qux.txt"

    assert tool.matches_line(env, line)

    call = tool.parse_line(env, line)
    assert isinstance(call, MoveToolCall)
    assert call._source == PurePosixPath("myproject/foo bar.txt")
    assert call._destination == PurePosixPath("myproject/baz qux.txt")

def test_move_tool_execute(env: Environment):
    call = MoveToolCall(PurePosixPath("myproject/a.txt"), PurePosixPath("myproject/b.txt"))
    call.execute(env)

    project = env[ProjectEnv].union
    assert project.read(PurePosixPath("myproject/a.txt")) is None
    assert project.read(PurePosixPath("myproject/b.txt")) == "content\n"

def test_move_tool_overwrite(env: Environment):
    project = env[ProjectEnv].union
    project.write(PurePosixPath("myproject/b.txt"), "old content")
    call = MoveToolCall(PurePosixPath("myproject/a.txt"), PurePosixPath("myproject/b.txt"))
    call.execute(env)
    log = env[ToolEnv].flush_log()
    assert "Warning: Overwriting ~/myproject/b.txt" in log
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

    with pytest.raises(ValueError, match="Path must start with ~/"):
        tool.parse_line(env, line)
