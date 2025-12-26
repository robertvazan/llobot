from pathlib import Path, PurePosixPath
from textwrap import dedent
import pytest
from llobot.environments import Environment
from llobot.environments.projects import ProjectEnv
from llobot.environments.tools import ToolEnv
from llobot.projects.directory import DirectoryProject
from llobot.projects.library.home import HomeProjectLibrary
from llobot.tools import InvalidToolCall, ToolCall
from llobot.tools.line import LineTool
from llobot.tools.move import MoveTool, MoveToolCall
from llobot.tools.remove import RemoveTool, RemoveToolCall
from llobot.tools.script import ScriptTool

@pytest.fixture
def env(tmp_path: Path) -> Environment:
    environment = Environment()
    # Register tools that script tool will use
    environment[ToolEnv].register(MoveTool())
    environment[ToolEnv].register(RemoveTool())
    return environment

def test_script_tool_slice_and_parse(env: Environment):
    tool = ScriptTool()
    text = dedent("""
        ```toolscript
        rm ~/a.txt
        mv ~/b.txt ~/c.txt
        ```
    """).strip()

    length = tool.slice(env, text, 0)
    assert length == len(text)

    calls = list(tool.parse(env, text))
    assert len(calls) == 2
    assert isinstance(calls[0], RemoveToolCall)
    assert isinstance(calls[1], MoveToolCall)

def test_script_tool_comments_and_empty_lines(env: Environment):
    tool = ScriptTool()
    text = dedent("""
        ```toolscript
        # This is a comment

        rm ~/a.txt
        ```
    """).strip()

    calls = list(tool.parse(env, text))
    assert len(calls) == 1
    assert isinstance(calls[0], RemoveToolCall)

def test_script_tool_invalid_command(env: Environment):
    tool = ScriptTool()
    text = dedent("""
        ```toolscript
        rm ~/a.txt
        unknown cmd
        ```
    """).strip()

    calls = list(tool.parse(env, text))
    assert len(calls) == 2
    assert isinstance(calls[0], RemoveToolCall)
    assert isinstance(calls[1], InvalidToolCall)
    assert "Unrecognized tool: unknown cmd" in str(calls[1]._error)

def test_script_tool_invalid_argument(env: Environment):
    tool = ScriptTool()
    text = dedent("""
        ```toolscript
        rm a.txt
        ```
    """).strip()

    calls = list(tool.parse(env, text))
    assert len(calls) == 1
    assert isinstance(calls[0], InvalidToolCall)
    assert "Path must start with ~/" in str(calls[0]._error)

def test_script_tool_matches_line_exception(env: Environment):
    class CrashingTool(LineTool):
        def matches_line(self, env: Environment, line: str) -> bool:
            if "crash" in line:
                raise ValueError("Crash!")
            return False

        def parse_line(self, env: Environment, line: str) -> ToolCall:
            raise NotImplementedError

    env[ToolEnv].register(CrashingTool())

    tool = ScriptTool()
    text = dedent("""
        ```toolscript
        crash this
        ```
    """).strip()

    calls = list(tool.parse(env, text))
    # Should fall through to Unrecognized tool, ignoring the crash
    assert len(calls) == 1
    assert isinstance(calls[0], InvalidToolCall)
    assert "Unrecognized tool: crash this" in str(calls[0]._error)
