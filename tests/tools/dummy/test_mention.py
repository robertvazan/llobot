from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.tools import ToolEnv
from llobot.tools.execution import execute_tool_calls
from llobot.tools.dummy.mention import DummyMentionTool
from llobot.chats.intent import ChatIntent

def test_mention_tool_warns_and_skips():
    env = Environment()
    env[ToolEnv].register(DummyMentionTool())

    source = "@mention some text\nNext line"

    # This should consume the first line
    execute_tool_calls(env, source)

    # Check context for status message
    context = env[ContextEnv].build()
    assert len(context) == 1
    message = context[0]
    assert message.intent == ChatIntent.STATUS
    assert "Mentions like `@mention` are not supported" in message.content

def test_quoted_mention():
    env = Environment()
    env[ToolEnv].register(DummyMentionTool())

    source = "@`quoted mention` rest of line"

    execute_tool_calls(env, source)

    context = env[ContextEnv].build()
    assert len(context) == 1
    assert "Mentions like `` @`quoted mention` `` are not supported" in context[0].content

def test_mention_with_leading_whitespace():
    env = Environment()
    env[ToolEnv].register(DummyMentionTool())

    source = "  @mention indented"

    execute_tool_calls(env, source)

    context = env[ContextEnv].build()
    assert len(context) == 1
    assert "Mentions like `@mention` are not supported" in context[0].content

def test_ignores_non_mention():
    env = Environment()
    env[ToolEnv].register(DummyMentionTool())

    source = "Just text"

    execute_tool_calls(env, source)

    context = env[ContextEnv].build()
    assert len(context) == 0
