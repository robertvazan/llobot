from pathlib import Path, PurePosixPath
from textwrap import dedent
import pytest
from llobot.environments import Environment
from llobot.environments.projects import ProjectEnv
from llobot.environments.tools import ToolEnv
from llobot.projects.directory import DirectoryProject
from llobot.projects.library.home import HomeProjectLibrary
from llobot.tools.remove import RemoveTool, RemoveToolCall

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

def test_remove_tool_matches_and_parses_line(env: Environment):
    tool = RemoveTool()
    line = "rm ~/myproject/a.txt"

    assert tool.matches_line(env, line)

    call = tool.parse_line(env, line)
    assert isinstance(call, RemoveToolCall)
    assert call._path == PurePosixPath("myproject/a.txt")

def test_remove_tool_quoted_path(env: Environment):
    tool = RemoveTool()
    line = "rm \"~/myproject/foo bar.txt\""

    assert tool.matches_line(env, line)

    call = tool.parse_line(env, line)
    assert isinstance(call, RemoveToolCall)
    assert call._path == PurePosixPath("myproject/foo bar.txt")

def test_remove_tool_execute(env: Environment):
    call = RemoveToolCall(PurePosixPath("myproject/a.txt"))
    call.execute(env)

    project = env[ProjectEnv].union
    assert project.read(PurePosixPath("myproject/a.txt")) is None

def test_remove_tool_no_match(env: Environment):
    tool = RemoveTool()
    assert not tool.matches_line(env, "del a")
    assert not tool.matches_line(env, "rm a b")
