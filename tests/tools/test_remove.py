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

def test_remove_tool_slice_and_parse():
    tool = RemoveTool()
    text = dedent("""
        ```tool
        rm ~/myproject/a.txt
        ```
    """).strip()

    length = tool.slice(text, 0)
    assert length == len(text)

    call = tool.parse(text)
    assert isinstance(call, RemoveToolCall)
    assert call._path == PurePosixPath("myproject/a.txt")

def test_remove_tool_execute(env: Environment):
    call = RemoveToolCall(PurePosixPath("myproject/a.txt"))
    call.execute(env)

    project = env[ProjectEnv].union
    assert project.read(PurePosixPath("myproject/a.txt")) is None
    log = env[ToolEnv].flush_log()
    assert "Removing ~/myproject/a.txt..." in log
    assert "File was removed." in log

def test_remove_tool_no_match():
    tool = RemoveTool()
    text = "```tool\nrm\n```"
    assert tool.slice(text, 0) == 0

def test_remove_tool_missing_tilde():
    tool = RemoveTool()
    text = "```tool\nrm myproject/a.txt\n```"
    with pytest.raises(ValueError, match="Path must start with ~/"):
        tool.parse(text.strip())
