from __future__ import annotations
from typing import Iterable
import pytest
from llobot.environments import Environment
from llobot.environments.tools import ToolEnv
from llobot.environments.context import ContextEnv
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.tools import InvalidToolCall, Tool, ToolCall
from llobot.tools.block import BlockTool

class MyToolCall(ToolCall):
    @property
    def summary(self) -> str:
        return "my tool call"

    def execute(self, env: Environment):
        pass

class MyTool(BlockTool):
    def slice(self, env: Environment, source: str, at: int) -> int:
        if source.startswith("TOOL", at):
            return 4
        return 0

    def parse(self, env: Environment, source: str) -> Iterable[ToolCall]:
        if source == "TOOL":
            yield MyToolCall()
            return
        raise ValueError("bad tool")

def test_try_parse_success():
    tool = MyTool()
    calls = list(tool.try_parse(Environment(), "TOOL"))
    assert len(calls) == 1
    assert isinstance(calls[0], MyToolCall)

def test_try_parse_error():
    tool = MyTool()
    calls = list(tool.try_parse(Environment(), "TOOL-bad"))
    assert len(calls) == 1
    assert isinstance(calls[0], InvalidToolCall)
    assert calls[0].summary == "invalid tool call"
    with pytest.raises(ValueError, match="bad tool"):
        calls[0].execute(Environment())

def test_try_execute_success():
    class SuccessToolCall(ToolCall):
        @property
        def summary(self) -> str: return "success"
        def execute(self, env: Environment): pass

    env = Environment()
    call = SuccessToolCall()
    assert call.try_execute(env)
    assert not env[ContextEnv].populated

def test_try_execute_failure():
    class FailToolCall(ToolCall):
        @property
        def summary(self) -> str: return "fail"
        def execute(self, env: Environment): raise ValueError("oops")

    env = Environment()
    call = FailToolCall()
    assert not call.try_execute(env)
    assert "Error executing fail: `oops`" in env[ContextEnv].build().messages[0].content
