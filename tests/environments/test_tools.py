from llobot.environments import Environment
from llobot.environments.tools import ToolEnv

def test_tool_env_log():
    env = Environment()
    tool_env = env[ToolEnv]

    tool_env.log("message 1")
    tool_env.log("message 2")

    assert tool_env.flush_log() == "message 1\nmessage 2"
    assert tool_env.flush_log() == ""
