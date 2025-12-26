from pathlib import Path, PurePosixPath
import pytest
from llobot.environments import Environment
from llobot.environments.projects import ProjectEnv
from llobot.environments.tools import ToolEnv
from llobot.formats.documents import standard_document_format
from llobot.projects.directory import DirectoryProject
from llobot.projects.library.home import HomeProjectLibrary
from llobot.tools.cat import CatTool, CatToolCall

@pytest.fixture
def home_library(tmp_path: Path) -> HomeProjectLibrary:
    return HomeProjectLibrary(str(tmp_path), mutable=True)

@pytest.fixture
def project(home_library: HomeProjectLibrary, tmp_path: Path) -> DirectoryProject:
    proj_dir = tmp_path / "myproject"
    proj_dir.mkdir()
    (proj_dir / "a.txt").write_text("content")
    (proj_dir / "b.py").write_text("print('hello')")
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

def test_cat_tool_matches_and_parses_line(env: Environment):
    tool = CatTool()
    line = "cat ~/myproject/a.txt"

    assert tool.matches_line(env, line)

    call = tool.parse_line(env, line)
    assert isinstance(call, CatToolCall)
    assert call._path == PurePosixPath("myproject/a.txt")

def test_cat_tool_execute(env: Environment):
    call = CatToolCall(PurePosixPath("myproject/a.txt"), standard_document_format())
    call.execute(env)

    log = env[ToolEnv].flush_log()
    output = env[ToolEnv].flush_output()

    assert "Reading ~/myproject/a.txt..." in log
    assert "File was read." in log

    assert "File: ~/myproject/a.txt" in output
    assert "content" in output
    assert "```" in output

def test_cat_tool_execute_python(env: Environment):
    call = CatToolCall(PurePosixPath("myproject/b.py"), standard_document_format())
    call.execute(env)

    output = env[ToolEnv].flush_output()
    # ExtensionLanguageMapping maps .py to python
    assert "```python" in output
    assert "print('hello')" in output

def test_cat_tool_missing_file(env: Environment):
    call = CatToolCall(PurePosixPath("myproject/nonexistent.txt"), standard_document_format())
    with pytest.raises(ValueError, match="File not found"):
        call.execute(env)

def test_cat_tool_no_match(env: Environment):
    tool = CatTool()
    assert not tool.matches_line(env, "read a")
    assert not tool.matches_line(env, "cat a b")
