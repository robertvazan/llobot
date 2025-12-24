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

def test_move_tool_slice_and_parse():
    tool = MoveTool()
    text = dedent("""
        ```tool
        mv ~/myproject/a.txt ~/myproject/b.txt
        ```
    """).strip()

    length = tool.slice(text, 0)
    assert length == len(text)

    call = tool.parse(text)
    assert isinstance(call, MoveToolCall)
    assert call._source == PurePosixPath("myproject/a.txt")
    assert call._destination == PurePosixPath("myproject/b.txt")

def test_move_tool_execute(env: Environment):
    call = MoveToolCall(PurePosixPath("myproject/a.txt"), PurePosixPath("myproject/b.txt"))
    call.execute(env)

    project = env[ProjectEnv].union
    assert project.read(PurePosixPath("myproject/a.txt")) is None
    assert project.read(PurePosixPath("myproject/b.txt")) == "content\n"
    log = env[ToolEnv].flush_log()
    assert "Moving ~/myproject/a.txt to ~/myproject/b.txt..." in log
    assert "File was moved." in log

def test_move_tool_overwrite(env: Environment):
    project = env[ProjectEnv].union
    project.write(PurePosixPath("myproject/b.txt"), "old content")
    call = MoveToolCall(PurePosixPath("myproject/a.txt"), PurePosixPath("myproject/b.txt"))
    call.execute(env)
    log = env[ToolEnv].flush_log()
    assert "Warning: Overwriting ~/myproject/b.txt" in log
    assert project.read(PurePosixPath("myproject/b.txt")) == "content\n"

def test_move_tool_no_match():
    tool = MoveTool()
    text = "```tool\nmv a.txt\n```"
    assert tool.slice(text, 0) == 0

def test_move_tool_missing_tilde():
    tool = MoveTool()
    text = "```tool\nmv myproject/a.txt ~/myproject/b.txt\n```"
    # FencedTool regex matches generic block, but parse should fail
    with pytest.raises(ValueError, match="Source path must start with ~/"):
        tool.parse(text.strip())
