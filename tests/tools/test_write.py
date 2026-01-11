import pytest
from pathlib import Path, PurePosixPath
from textwrap import dedent
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.projects import ProjectEnv
from llobot.projects.directory import DirectoryProject
from llobot.projects.library.predefined import PredefinedProjectLibrary
from llobot.tools.write import WriteTool, WriteToolCall

@pytest.fixture
def project(tmp_path: Path) -> DirectoryProject:
    proj_dir = tmp_path / "myproject"
    proj_dir.mkdir()
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

def test_write_tool_slice_and_parse(env: Environment):
    tool = WriteTool()
    text = dedent("""
        <details>
        <summary>Write: ~/myproject/foo.txt</summary>

        ```
        content
        of the file
        ```

        </details>
    """).strip()

    length = tool.slice(env, text, 0)
    assert length == len(text)

    calls = list(tool.parse(env, text))
    assert len(calls) == 1
    call = calls[0]
    assert isinstance(call, WriteToolCall)
    assert call._path == "~/myproject/foo.txt"
    assert call._content == "content\nof the file\n"

    call.execute(env)
    project = env[ProjectEnv].union
    assert project.read(PurePosixPath("myproject/foo.txt")) == "content\nof the file\n"
    assert "Written ~/myproject/foo.txt" in env[ContextEnv].build().messages[0].content

def test_write_tool_slice_extra_whitespace(env: Environment):
    tool = WriteTool()
    text = dedent("""
        <details>
          <summary>  Write:   ~/myproject/bar.py   </summary>

        ````python
        print("hello")
        ````

        </details>
    """).strip()

    length = tool.slice(env, text, 0)
    assert length == len(text)

    calls = list(tool.parse(env, text))
    assert len(calls) == 1
    call = calls[0]
    assert isinstance(call, WriteToolCall)
    assert call._path == "~/myproject/bar.py"
    assert call._content == 'print("hello")\n'

def test_write_tool_no_match(env: Environment):
    tool = WriteTool()
    text = "<summary>Write: foo.txt</summary>"
    assert tool.slice(env, text, 0) == 0

def test_write_tool_missing_tilde_prefix(env: Environment):
    tool = WriteTool()
    text = dedent("""
        <details>
        <summary>Write: myproject/foo.txt</summary>
        ```
        ```
        </details>
    """).strip()

    # Slice matches regex, and parse succeeds, but execute should fail
    length = tool.slice(env, text, 0)
    assert length == len(text)

    calls = list(tool.parse(env, text))
    assert len(calls) == 1
    with pytest.raises(ValueError, match="Path must start with ~/"):
        calls[0].execute(env)

def test_write_tool_empty_code_block(env: Environment):
    tool = WriteTool()
    text = dedent("""
        <details>
        <summary>Write: ~/myproject/empty.txt</summary>
        ```
        ```
        </details>
    """).strip()

    length = tool.slice(env, text, 0)
    assert length == len(text)

    calls = list(tool.parse(env, text))
    assert len(calls) == 1
    call = calls[0]
    assert isinstance(call, WriteToolCall)
    assert call._path == "~/myproject/empty.txt"
    assert call._content == ""

    call.execute(env)
    project = env[ProjectEnv].union
    assert project.read(PurePosixPath("myproject/empty.txt")) == ""

def test_write_tool_nested_fences(env: Environment):
    tool = WriteTool()
    # Outer fence is 4 backticks, inner is 3. Should pass.
    text = dedent("""
        <details>
        <summary>Write: ~/myproject/foo.md</summary>

        ````markdown
        ```python
        print("hello")
        ```
        ````

        </details>
    """).strip()

    calls = list(tool.parse(env, text))
    assert len(calls) == 1
    assert calls[0]._content.strip() == '```python\nprint("hello")\n```'

def test_write_tool_conflicting_fence(env: Environment):
    tool = WriteTool()
    text = dedent("""
        <details>
        <summary>Write: ~/myproject/foo.md</summary>

        ```markdown
        Start
        ```
        End
        ```

        </details>
    """).strip()

    calls = list(tool.parse(env, text))
    assert len(calls) == 1
    with pytest.raises(ValueError, match="Content contains a line starting with"):
        calls[0].execute(env)

def test_write_tool_midline_fence(env: Environment):
    tool = WriteTool()
    text = dedent("""
        <details>
        <summary>Write: ~/myproject/foo.md</summary>

        ```markdown
        Here is some text with ``` backticks in the middle.
        ```

        </details>
    """).strip()

    calls = list(tool.parse(env, text))
    assert len(calls) == 1
    assert "text with ``` backticks" in calls[0]._content
