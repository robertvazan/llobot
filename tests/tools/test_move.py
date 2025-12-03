from pathlib import Path
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

def test_move_tool_slice_and_parse():
    tool = MoveTool()
    text = dedent("""
        ```tool
        mv myproject/a.txt myproject/b.txt
        ```
    """).strip()

    length = tool.slice(text, 0)
    assert length == len(text)

    call = tool.parse(text)
    assert isinstance(call, MoveToolCall)
    assert call._source == Path("myproject/a.txt")
    assert call._destination == Path("myproject/b.txt")

def test_move_tool_execute(env: Environment):
    call = MoveToolCall(Path("myproject/a.txt"), Path("myproject/b.txt"))
    call.execute(env)

    project = env[ProjectEnv].union
    assert project.read(Path("myproject/a.txt")) is None
    assert project.read(Path("myproject/b.txt")) == "content\n"
    log = env[ToolEnv].flush_log()
    assert "Moving myproject/a.txt to myproject/b.txt..." in log
    assert "File was moved." in log

def test_move_tool_overwrite(env: Environment):
    project = env[ProjectEnv].union
    project.write(Path("myproject/b.txt"), "old content")
    call = MoveToolCall(Path("myproject/a.txt"), Path("myproject/b.txt"))
    call.execute(env)
    log = env[ToolEnv].flush_log()
    assert "Warning: Overwriting myproject/b.txt" in log
    assert project.read(Path("myproject/b.txt")) == "content\n"

def test_move_tool_no_match():
    tool = MoveTool()
    text = "```tool\nmv a.txt\n```"
    assert tool.slice(text, 0) == 0
