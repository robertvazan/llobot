from llobot.environments import Environment
from llobot.environments.tools import ToolEnv
from llobot.tools.block import BlockTool
from llobot.tools.dummy import DummyTool

class MyBlockTool(BlockTool):
    def slice(self, env, source, at): return 0
    def parse(self, env, source): return None

class MyDummyTool(DummyTool):
    def skip(self, env, source, at): return 0

def test_tool_registry():
    env = Environment()
    tool_env = env[ToolEnv]

    t1 = MyBlockTool()
    t2 = MyDummyTool()
    t3 = MyBlockTool() # Equal to t1 if no fields

    tool_env.register(t1)
    tool_env.register(t2)
    tool_env.register(t3)

    tools = tool_env.tools
    assert len(tools) == 2
    assert t1 in tools
    assert t2 in tools
    assert tools[-1] == t2 # Dummy tool last

def test_tool_register_all():
    env = Environment()
    tool_env = env[ToolEnv]

    t1 = MyBlockTool()
    t2 = MyDummyTool()

    tool_env.register_all([t1, t2])

    tools = tool_env.tools
    assert len(tools) == 2
    assert t1 in tools
    assert t2 in tools

def test_tool_env_caching():
    env = Environment()
    tool_env = env[ToolEnv]

    t1 = MyBlockTool()
    tool_env.register(t1)

    tools1 = tool_env.tools
    tools2 = tool_env.tools
    assert tools1 is tools2

    t2 = MyDummyTool()
    tool_env.register(t2)
    tools3 = tool_env.tools
    assert tools3 is not tools1
    assert len(tools3) == 2
