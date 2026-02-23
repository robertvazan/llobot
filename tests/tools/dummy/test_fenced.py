from textwrap import dedent
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.tools import ToolEnv
from llobot.tools.execution import execute_tool_calls
from llobot.tools.dummy.fenced import UnrecognizedFencedTool
from llobot.chats.intent import ChatIntent

def test_unrecognized_tool_reports_error():
    env = Environment()
    env[ToolEnv].register(UnrecognizedFencedTool())

    source = dedent("""
        <details>
        <summary>Unknown: some header</summary>

        ```
        some content
        ```

        </details>
    """).strip()

    # Parse tools - this should trigger the skip method of UnrecognizedFencedTool
    execute_tool_calls(env, source)

    # Check context for status message
    context = env[ContextEnv].build()
    assert len(context) == 1
    message = context[0]
    assert message.intent == ChatIntent.SYSTEM
    assert "Unrecognized tool 'Unknown' or invalid block format. Header: `some header`" in message.content

def test_unrecognized_tool_ignores_non_fenced_blocks():
    env = Environment()
    env[ToolEnv].register(UnrecognizedFencedTool())

    source = "Some random text"

    execute_tool_calls(env, source)

    context = env[ContextEnv].build()
    assert len(context) == 0

def test_unrecognized_tool_header_with_special_chars():
    env = Environment()
    env[ToolEnv].register(UnrecognizedFencedTool())

    source = dedent("""
        <details>
        <summary>Unknown: header `with` backticks</summary>

        ```
        some content
        ```

        </details>
    """).strip()

    execute_tool_calls(env, source)

    context = env[ContextEnv].build()
    assert len(context) == 1
    message = context[0]
    assert "Unrecognized tool 'Unknown' or invalid block format. Header: ``header `with` backticks``" in message.content
