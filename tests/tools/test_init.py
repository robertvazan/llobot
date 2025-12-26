from __future__ import annotations
import pytest
from llobot.environments import Environment
from llobot.environments.tools import ToolEnv
from llobot.tools import InvalidToolCall, Tool, ToolCall
from llobot.tools.block import BlockTool

class MyToolCall(ToolCall):
    @property
    def title(self) -> str:
        return "my tool call"

    def execute(self, env: Environment):
        pass

class MyTool(BlockTool):
    def slice(self, env: Environment, source: str, at: int) -> int:
        if source.startswith("TOOL", at):
            return 4
        return 0

    def parse(self, env: Environment, source: str) -> ToolCall | None:
        if source == "TOOL":
            return MyToolCall()
        raise ValueError("bad tool")

def test_try_parse_success():
    tool = MyTool()
    call = tool.try_parse(Environment(), "TOOL")
    assert isinstance(call, MyToolCall)

def test_try_parse_error():
    tool = MyTool()
    call = tool.try_parse(Environment(), "TOOL-bad")
    assert isinstance(call, InvalidToolCall)
    assert call.title == "invalid tool call"
    with pytest.raises(ValueError, match="bad tool"):
        call.execute(Environment())

def test_try_execute_success():
    class SuccessToolCall(ToolCall):
        @property
        def title(self) -> str: return "success"
        def execute(self, env: Environment): pass

    env = Environment()
    call = SuccessToolCall()
    assert call.try_execute(env)
    assert not env[ToolEnv].flush_log()

def test_try_execute_failure():
    class FailToolCall(ToolCall):
        @property
        def title(self) -> str: return "fail"
        def execute(self, env: Environment): raise ValueError("oops")

    env = Environment()
    call = FailToolCall()
    assert not call.try_execute(env)
    assert "Error executing: oops" in env[ToolEnv].flush_log()
