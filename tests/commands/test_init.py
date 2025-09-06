import pytest
from llobot.environments import Environment
from llobot.environments.command_queue import CommandQueueEnv
from llobot.commands import Command

class MockCommand(Command):
    def __init__(self, text_to_handle: str | list[str] | None = None):
        if text_to_handle is None:
            self.texts_to_handle = set()
        elif isinstance(text_to_handle, str):
            self.texts_to_handle = {text_to_handle}
        else:
            self.texts_to_handle = set(text_to_handle)
        self.handled_commands = []
        self.process_called = False

    def handle(self, text: str, env: Environment) -> bool:
        if text in self.texts_to_handle:
            self.handled_commands.append(text)
            return True
        return False

    def process(self, env: Environment):
        self.process_called = True

def test_command_handle_default():
    """Tests that Command.handle returns False by default."""
    cmd = Command()
    env = Environment()
    assert not cmd.handle("some command", env)

def test_command_process_default():
    """Tests that Command.process does nothing by default."""
    cmd = Command()
    env = Environment()
    cmd.process(env) # Should not raise

def test_command_handle_pending():
    """Tests Command.handle_pending."""
    cmd = MockCommand(["cmd1", "cmd3"])
    env = Environment()
    queue = env[CommandQueueEnv]
    queue.add(["cmd1", "cmd2", "cmd3"])

    cmd.handle_pending(env)

    # Check that correct commands were handled
    assert sorted(cmd.handled_commands) == ["cmd1", "cmd3"]
    # Check that handled commands were consumed from the queue
    assert queue.get() == ["cmd2"]
    # Check that process was called
    assert cmd.process_called

def test_command_handle_pending_empty_queue():
    """Tests Command.handle_pending with an empty queue."""
    cmd = MockCommand("cmd1")
    env = Environment()

    cmd.handle_pending(env)

    assert cmd.handled_commands == []
    assert env[CommandQueueEnv].get() == []
    assert cmd.process_called
