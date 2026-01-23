from __future__ import annotations
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.tools import ToolEnv
from llobot.tools.block import BlockTool
from llobot.tools.reader import ToolReader
from llobot.tools.execution import execute_tool_calls

class ExecutionTestEnv:
    def __init__(self):
        self.executed: list[str] = []
        self.state: int = 0
        self.read_value: int | None = None

class SimpleTool(BlockTool):
    def execute(self, env: Environment, reader: ToolReader) -> None:
        source = reader.source
        at = reader.position
        if source.startswith("CMD:", at):
            try:
                end = source.index("\n", at)
                length = end - at
            except ValueError:
                length = len(source) - at

            content = source[at+4:at+length].strip()

            reader.advance(length)

            if content == "fail":
                raise Exception("oops")

            env[ExecutionTestEnv].executed.append(content)
            reader.passed()

def test_execute_tool_calls_success():
    env = Environment()
    env[ToolEnv].register(SimpleTool())

    source = "CMD:one\nCMD:two"
    count = execute_tool_calls(env, source)

    assert count == 2
    assert env[ExecutionTestEnv].executed == ["one", "two"]

    context = env[ContextEnv].build()
    assert len(context) == 1
    assert "✅ All 2 tool calls executed." in context[0].content

def test_execute_tool_calls_partial_failure():
    env = Environment()
    env[ToolEnv].register(SimpleTool())

    source = "CMD:one\nCMD:fail\nCMD:two"
    count = execute_tool_calls(env, source)

    assert count == 3
    assert env[ExecutionTestEnv].executed == ["one", "two"]

    context = env[ContextEnv].build()
    # 1 failure status + 1 summary status
    assert len(context) == 2
    assert "Error executing tool: `oops`" in context[0].content
    assert "❌ 2 of 3 tool calls executed." in context[1].content

def test_execute_tool_calls_none():
    env = Environment()
    env[ToolEnv].register(SimpleTool())

    source = "nothing here"
    count = execute_tool_calls(env, source)

    assert count == 0

    context = env[ContextEnv].build()
    assert len(context) == 0

def test_execute_tool_calls_interleaved():
    """
    Verify that tools are executed as they are parsed, not all at once at the end.
    We'll use a side effect that affects subsequent tools.
    """
    class StateTool(BlockTool):
        def execute(self, env, reader) -> None:
            source = reader.source
            at = reader.position
            if source.startswith("OP:", at):
                try:
                    end = source.index("\n", at)
                    length = end - at
                except ValueError:
                    length = len(source) - at

                action = source[at+3:at+length].strip()
                reader.advance(length)

                test_env = env[ExecutionTestEnv]
                if action == "read":
                    test_env.read_value = test_env.state
                elif action == "inc":
                    test_env.state += 1

                reader.passed()

    env = Environment()
    env[ToolEnv].register(StateTool())

    # Sequence: Read (0) -> Inc (1) -> Read (1)
    source = "OP:read\nOP:inc\nOP:read"
    execute_tool_calls(env, source)

    test_env = env[ExecutionTestEnv]

    # Since we overwrite read_value, checking if it is 1 proves that the second read
    # happened after inc was executed.
    assert test_env.state == 1
    assert test_env.read_value == 1
