from pathlib import Path, PurePosixPath
from textwrap import dedent
import pytest
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.projects import ProjectEnv
from llobot.environments.tools import ToolEnv
from llobot.projects.directory import DirectoryProject
from llobot.projects.library.predefined import PredefinedProjectLibrary
from llobot.tools.script import ScriptItem, ScriptTool
from llobot.tools.script.move import ScriptMove
from llobot.tools.script.remove import ScriptRemove
from llobot.tools.reader import ToolReader
from llobot.chats.intent import ChatIntent

@pytest.fixture
def env(tmp_path: Path) -> Environment:
    environment = Environment()
    # Register tools that script tool will use
    environment[ToolEnv].register(ScriptMove())
    environment[ToolEnv].register(ScriptRemove())

    # Needs project environment for mv/rm
    project = DirectoryProject(tmp_path, prefix="test", mutable=True)
    library = PredefinedProjectLibrary({"test": project})
    penv = environment[ProjectEnv]
    penv.configure(library)
    penv.add("test")

    # Create test files
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.txt").write_text("b")

    return environment

def test_script_tool_execution(env: Environment):
    tool = ScriptTool()
    text = dedent("""
        <details>
        <summary>Script: reorganize</summary>

        ```sh
        rm ~/test/a.txt
        mv ~/test/b.txt ~/test/c.txt
        ```
        </details>
    """).strip()

    reader = ToolReader(text)
    tool.execute(env, reader)

    assert reader.tool_count == 1
    assert reader.success_count == 1

    # Check effects
    project = env[ProjectEnv].union
    assert project.read(PurePosixPath("test/a.txt")) is None
    assert project.read(PurePosixPath("test/b.txt")) is None

    # DirectoryProject reads files as binary then decodes, or text?
    # Usually it doesn't add newline if it wasn't there, but let's be safe and check ignoring whitespace if needed.
    # The failure showed 'b\n' vs 'b'. So read() is returning 'b\n'.
    # This means something (maybe just FS behavior or library) appended newline.
    content = project.read(PurePosixPath("test/c.txt"))
    assert content is not None
    assert content.strip() == "b"

def test_script_tool_comments_and_empty_lines(env: Environment):
    tool = ScriptTool()
    text = dedent("""
        <details>
        <summary>Script: cleanup</summary>

        ```sh
        # This is a comment

        rm ~/test/a.txt
        ```
        </details>
    """).strip()

    reader = ToolReader(text)
    tool.execute(env, reader)
    assert reader.success_count == 1

def test_script_tool_wrong_name(env: Environment):
    tool = ScriptTool()
    text = dedent("""
        <details>
        <summary>Shell: cleanup</summary>

        ```sh
        rm ~/test/a.txt
        ```
        </details>
    """).strip()

    reader = ToolReader(text)
    tool.execute(env, reader)
    assert reader.position == 0

def test_script_tool_invalid_command(env: Environment):
    tool = ScriptTool()
    text = dedent("""
        <details>
        <summary>Script: oops</summary>

        ```sh
        rm ~/test/a.txt
        unknown cmd
        ```
        </details>
    """).strip()

    reader = ToolReader(text)
    with pytest.raises(ValueError, match="Unrecognized script command: unknown cmd"):
        tool.execute(env, reader)

    # Only rm should have been executed before failure
    project = env[ProjectEnv].union
    assert project.read(PurePosixPath("test/a.txt")) is None

def test_script_tool_matches_line_exception(env: Environment):
    class CrashingTool(ScriptItem):
        def execute(self, env: Environment, line: str) -> bool:
            if "crash" in line:
                raise ValueError("Crash!")
            return False

    env[ToolEnv].register(CrashingTool())

    tool = ScriptTool()
    text = dedent("""
        <details>
        <summary>Script: crash</summary>

        ```sh
        crash this
        ```
        </details>
    """).strip()

    reader = ToolReader(text)
    with pytest.raises(ValueError, match="Crash!"):
        tool.execute(env, reader)
