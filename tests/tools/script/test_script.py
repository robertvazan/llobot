from pathlib import Path
from textwrap import dedent
import pytest
from llobot.environments import Environment
from llobot.environments.tools import ToolEnv
from llobot.tools import InvalidToolCall, ToolCall
from llobot.tools.script import ScriptItem, ScriptTool
from llobot.tools.script.move import ScriptMove, ScriptMoveCall
from llobot.tools.script.remove import ScriptRemove, ScriptRemoveCall

@pytest.fixture
def env(tmp_path: Path) -> Environment:
    environment = Environment()
    # Register tools that script tool will use
    environment[ToolEnv].register(ScriptMove())
    environment[ToolEnv].register(ScriptRemove())
    return environment

def test_script_tool_slice_and_parse(env: Environment):
    tool = ScriptTool()
    text = dedent("""
        <details>
        <summary>Script: reorganize</summary>

        ```sh
        rm ~/a.txt
        mv ~/b.txt ~/c.txt
        ```
        </details>
    """).strip()

    length = tool.slice(env, text, 0)
    assert length == len(text)

    calls = list(tool.parse(env, text))
    assert len(calls) == 2
    assert isinstance(calls[0], ScriptRemoveCall)
    assert isinstance(calls[1], ScriptMoveCall)

def test_script_tool_comments_and_empty_lines(env: Environment):
    tool = ScriptTool()
    text = dedent("""
        <details>
        <summary>Script: cleanup</summary>

        ```sh
        # This is a comment

        rm ~/a.txt
        ```
        </details>
    """).strip()

    calls = list(tool.parse(env, text))
    assert len(calls) == 1
    assert isinstance(calls[0], ScriptRemoveCall)

def test_script_tool_wrong_name(env: Environment):
    tool = ScriptTool()
    text = dedent("""
        <details>
        <summary>Shell: cleanup</summary>

        ```sh
        rm ~/a.txt
        ```
        </details>
    """).strip()

    length = tool.slice(env, text, 0)
    assert length == 0

def test_script_tool_invalid_command(env: Environment):
    tool = ScriptTool()
    text = dedent("""
        <details>
        <summary>Script: oops</summary>

        ```sh
        rm ~/a.txt
        unknown cmd
        ```
        </details>
    """).strip()

    calls = list(tool.parse(env, text))
    assert len(calls) == 2
    assert isinstance(calls[0], ScriptRemoveCall)
    assert isinstance(calls[1], InvalidToolCall)
    assert "Unrecognized tool: unknown cmd" in str(calls[1]._error)

def test_script_tool_matches_line_exception(env: Environment):
    class CrashingTool(ScriptItem):
        def matches(self, env: Environment, line: str) -> bool:
            if "crash" in line:
                raise ValueError("Crash!")
            return False

        def parse(self, env: Environment, line: str) -> ToolCall:
            raise NotImplementedError

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

    calls = list(tool.parse(env, text))
    # Should fall through to Unrecognized tool, ignoring the crash
    assert len(calls) == 1
    assert isinstance(calls[0], InvalidToolCall)
    assert "Unrecognized tool: crash this" in str(calls[0]._error)
