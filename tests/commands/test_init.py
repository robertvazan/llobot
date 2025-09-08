import pytest
from llobot.environments import Environment
from llobot.environments.commands import CommandsEnv
from llobot.commands import Command, Step

def test_step_process_default():
    """Tests that Step.process does nothing by default."""
    step = Step()
    env = Environment()
    step.process(env) # Should not raise

def test_command_handle_default():
    """Tests that Command.handle returns False by default."""
    cmd = Command()
    env = Environment()
    assert not cmd.handle("some command", env)

class MockCommand(Command):
    def __init__(self, text_to_handle: str | list[str] | None = None):
        if text_to_handle is None:
            self.texts_to_handle = set()
        elif isinstance(text_to_handle, str):
            self.texts_to_handle = {text_to_handle}
        else:
            self.texts_to_handle = set(text_to_handle)
        self.handled_commands = []

    def handle(self, text: str, env: Environment) -> bool:
        if text in self.texts_to_handle:
            self.handled_commands.append(text)
            return True
        return False

def test_command_process():
    """Tests Command.process."""
    cmd = MockCommand(["cmd1", "cmd3"])
    env = Environment()
    queue = env[CommandsEnv]
    queue.add(["cmd1", "cmd2", "cmd3"])

    cmd.process(env)

    # Check that correct commands were handled
    assert sorted(cmd.handled_commands) == ["cmd1", "cmd3"]
    # Check that handled commands were consumed from the queue
    assert queue.get() == ["cmd2"]

def test_command_process_empty_queue():
    """Tests Command.process with an empty queue."""
    cmd = MockCommand("cmd1")
    env = Environment()

    cmd.process(env)

    assert cmd.handled_commands == []
    assert env[CommandsEnv].get() == []
