import pytest
from textwrap import dedent
from typing import Iterable
from llobot.environments import Environment
from llobot.environments.tools import ToolEnv
from llobot.tools import Tool, ToolCall
from llobot.tools.block import BlockTool
from llobot.tools.parsing import parse_tool_calls

class SimpleToolCall(ToolCall):
    def __init__(self, content):
        self.content = content

    @property
    def title(self):
        return f"simple {self.content}"

    def execute(self, env):
        pass

class SimpleTool(BlockTool):
    def slice(self, env, source, at):
        if source.startswith("CMD:", at):
            try:
                end = source.index("\n", at)
                return end - at
            except ValueError:
                return len(source) - at
        return 0

    def parse(self, env, formatted) -> Iterable[ToolCall]:
        yield SimpleToolCall(formatted[4:])

def test_parse_tool_calls_basic():
    text = dedent("""
        CMD:one
        ignored
        CMD:two
    """).lstrip()
    env = Environment()
    env[ToolEnv].register(SimpleTool())

    calls = list(parse_tool_calls(env, text))

    assert len(calls) == 2
    assert isinstance(calls[0], SimpleToolCall)
    assert calls[0].content == "one"
    assert calls[1].content == "two"

def test_parse_tool_calls_no_newline_at_end():
    text = "CMD:one"
    env = Environment()
    env[ToolEnv].register(SimpleTool())

    calls = list(parse_tool_calls(env, text))
    assert len(calls) == 1
    assert calls[0].content == "one"

def test_parse_tool_calls_skips_none():
    class NoneTool(BlockTool):
        def slice(self, env, source, at):
            if source.startswith("SKIP", at):
                return 4
            return 0
        def parse(self, env, source):
            return [] # Empty iterable

    text = dedent("""
        CMD:one
        SKIP
        CMD:two
    """).lstrip()
    env = Environment()
    env[ToolEnv].register(SimpleTool())
    env[ToolEnv].register(NoneTool())

    calls = list(parse_tool_calls(env, text))

    assert len(calls) == 2
    assert calls[0].content == "one"
    assert calls[1].content == "two"

def test_skip_non_matching_lines():
    text = dedent("""
        Line 1
        CMD:foo
        Line 3
    """).lstrip()
    env = Environment()
    env[ToolEnv].register(SimpleTool())

    calls = list(parse_tool_calls(env, text))
    assert len(calls) == 1
    assert calls[0].content == "foo"

def test_parse_tool_calls_no_extra_line_skip():
    class LineEatingTool(BlockTool):
        def slice(self, env, source, at):
            if source.startswith("CMD:", at):
                try:
                    end = source.index("\n", at)
                    return end - at + 1 # eats the newline
                except ValueError:
                    return len(source) - at
            return 0
        def parse(self, env, formatted):
            yield SimpleToolCall(formatted[4:].strip())

    text = dedent("""
        CMD:one
        CMD:two
    """).lstrip()
    env = Environment()
    env[ToolEnv].register(LineEatingTool())

    calls = list(parse_tool_calls(env, text))
    assert len(calls) == 2
    assert calls[0].content == "one"
    assert calls[1].content == "two"
