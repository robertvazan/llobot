import pytest
from pathlib import Path
from textwrap import dedent
from llobot.environments import Environment
from llobot.environments.projects import ProjectEnv
from llobot.environments.tools import ToolEnv
from llobot.projects.directory import DirectoryProject
from llobot.projects.library.home import HomeProjectLibrary
from llobot.tools.files import FileTool, FileToolCall

@pytest.fixture
def home_library(tmp_path: Path) -> HomeProjectLibrary:
    return HomeProjectLibrary(str(tmp_path), mutable=True)

@pytest.fixture
def project(home_library: HomeProjectLibrary, tmp_path: Path) -> DirectoryProject:
    proj_dir = tmp_path / "myproject"
    proj_dir.mkdir()
    # Looking up the project will create it via the library.
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

def test_file_tool_slice_and_parse(env: Environment):
    tool = FileTool()
    text = dedent("""
        <details>
        <summary>File: myproject/foo.txt</summary>

        ```
        content
        of the file
        ```

        </details>
    """).strip()

    length = tool.slice(text, 0)
    assert length == len(text)

    call = tool.parse(text)
    assert isinstance(call, FileToolCall)
    assert call._path == Path("myproject/foo.txt")
    assert call._content == "content\nof the file\n"

    call.execute(env)
    project = env[ProjectEnv].union
    assert project.read(Path("myproject/foo.txt")) == "content\nof the file\n"

    log = env[ToolEnv].flush_log()
    assert "Writing myproject/foo.txt..." in log
    assert "File was written." in log

def test_file_tool_slice_extra_whitespace(env: Environment):
    tool = FileTool()
    text = dedent("""
        <details>
          <summary>  File:   myproject/bar.py   </summary>

        ````python
        print("hello")
        ````

        </details>
    """).strip()

    length = tool.slice(text, 0)
    assert length == len(text)

    call = tool.parse(text)
    assert isinstance(call, FileToolCall)
    assert call._path == Path("myproject/bar.py")
    assert call._content == 'print("hello")\n'

def test_file_tool_no_match():
    tool = FileTool()
    text = "<summary>File: foo.txt</summary>"
    assert tool.slice(text, 0) == 0

def test_file_tool_empty_code_block(env: Environment):
    tool = FileTool()
    text = dedent("""
        <details>
        <summary>File: myproject/empty.txt</summary>
        ```
        ```
        </details>
    """).strip()

    length = tool.slice(text, 0)
    assert length == len(text)

    call = tool.parse(text)
    assert isinstance(call, FileToolCall)
    assert call._path == Path("myproject/empty.txt")
    assert call._content == ""

    call.execute(env)
    project = env[ProjectEnv].union
    assert project.read(Path("myproject/empty.txt")) == ""
