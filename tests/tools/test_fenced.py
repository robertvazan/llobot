from textwrap import dedent
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.tools import ToolEnv
from llobot.tools.fenced import UnrecognizedFencedTool
from llobot.tools.parsing import parse_tool_calls
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
    list(parse_tool_calls(env, source))

    # Check context for status message
    context = env[ContextEnv].build()
    assert len(context) == 1
    message = context[0]
    assert message.intent == ChatIntent.STATUS
    assert "Unrecognized tool 'Unknown' or invalid block format. Header: some header" in message.content

def test_unrecognized_tool_ignores_non_fenced_blocks():
    env = Environment()
    env[ToolEnv].register(UnrecognizedFencedTool())

    source = "Some random text"

    list(parse_tool_calls(env, source))

    context = env[ContextEnv].build()
    assert len(context) == 0
