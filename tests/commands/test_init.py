import pytest
from llobot.environments import Environment
from llobot.environments.commands import CommandsEnv
from llobot.commands import handle_commands

def test_handle_commands():
    """Tests Command.process."""
    handled_commands = []
    def handler(text: str, env: Environment) -> bool:
        if text in ["cmd1", "cmd3"]:
            handled_commands.append(text)
            return True
        return False

    env = Environment()
    queue = env[CommandsEnv]
    queue.add(["cmd1", "cmd2", "cmd3"])

    handle_commands(env, handler)

    # Check that correct commands were handled
    assert sorted(handled_commands) == ["cmd1", "cmd3"]
    # Check that handled commands were consumed from the queue
    assert queue.get() == ["cmd2"]

def test_handle_commands_empty_queue():
    """Tests Command.process with an empty queue."""
    handled_commands = []
    def handler(text: str, env: Environment) -> bool:
        handled_commands.append(text)
        return True

    env = Environment()
    handle_commands(env, handler)

    assert handled_commands == []
    assert env[CommandsEnv].get() == []
