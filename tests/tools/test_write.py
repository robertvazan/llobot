import pytest
from pathlib import Path, PurePosixPath
from textwrap import dedent
from llobot.chats.intent import ChatIntent
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.projects import ProjectEnv
from llobot.projects.directory import DirectoryProject
from llobot.projects.library.predefined import PredefinedProjectLibrary
from llobot.tools.write import WriteTool
from llobot.tools.reader import ToolReader

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

def test_write_tool_execution(env: Environment):
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

    reader = ToolReader(text)
    tool.execute(env, reader)
    assert reader.success_count == 1

    project = env[ProjectEnv].union
    assert project.read(PurePosixPath("myproject/foo.txt")) == "content\nof the file\n"

    messages = env[ContextEnv].build().messages
    assert any("Written `~/myproject/foo.txt`" in m.content for m in messages)

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

    reader = ToolReader(text)
    tool.execute(env, reader)
    assert reader.success_count == 1

    project = env[ProjectEnv].union
    assert 'print("hello")' in project.read(PurePosixPath("myproject/bar.py"))

def test_write_tool_no_match(env: Environment):
    tool = WriteTool()
    text = "<summary>Write: foo.txt</summary>"

    reader = ToolReader(text)
    tool.execute(env, reader)
    assert reader.position == 0

def test_write_tool_missing_tilde_prefix(env: Environment):
    tool = WriteTool()
    text = dedent("""
        <details>
        <summary>Write: myproject/foo.txt</summary>
        ```python
        ```
        </details>
    """).strip()

    reader = ToolReader(text)
    with pytest.raises(ValueError, match="Path must start with ~/"):
        tool.execute(env, reader)

def test_write_tool_empty_code_block(env: Environment):
    tool = WriteTool()
    text = dedent("""
        <details>
        <summary>Write: ~/myproject/empty.txt</summary>
        ```text
        ```
        </details>
    """).strip()

    reader = ToolReader(text)
    tool.execute(env, reader)

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

    reader = ToolReader(text)
    tool.execute(env, reader)

    project = env[ProjectEnv].union
    assert '```python\nprint("hello")\n```' in project.read(PurePosixPath("myproject/foo.md"))

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

    reader = ToolReader(text)
    with pytest.raises(ValueError, match="Content contains a line starting with"):
        tool.execute(env, reader)

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

    reader = ToolReader(text)
    tool.execute(env, reader)

    project = env[ProjectEnv].union
    assert "text with ``` backticks" in project.read(PurePosixPath("myproject/foo.md"))

def test_write_tool_file_alias_warning(env: Environment):
    tool = WriteTool()
    text = dedent("""
        <details>
        <summary>File: ~/myproject/foo.txt</summary>

        ```
        content
        ```

        </details>
    """).strip()

    reader = ToolReader(text)
    tool.execute(env, reader)
    assert reader.success_count == 1

    project = env[ProjectEnv].union
    assert project.read(PurePosixPath("myproject/foo.txt")) == "content\n"

    messages = env[ContextEnv].build().messages
    assert any(m.intent == ChatIntent.SYSTEM and "Warning: Use 'Write' tool" in m.content for m in messages)
    assert any(m.intent == ChatIntent.STATUS and "Written `~/myproject/foo.txt`" in m.content for m in messages)
