import pytest
from llobot.environments import Environment
from llobot.environments.command_queue import CommandQueueEnv
from llobot.commands import Command
from llobot.commands.chains import CommandChain

class MockCommand(Command):
    def __init__(self, texts_to_handle: list[str] | None = None):
        self.texts_to_handle = set(texts_to_handle or [])
        self.handle_pending_called = False

    def handle(self, text: str, env: Environment) -> bool:
        return text in self.texts_to_handle

    def handle_pending(self, env: Environment):
        # Override to just record call, for simplicity in chain tests
        self.handle_pending_called = True

def test_command_chain_empty():
    """Tests that an empty CommandChain does nothing."""
    chain = CommandChain()
    env = Environment()
    chain.handle_pending(env) # Should not raise

def test_command_chain_calls_all():
    """Tests that CommandChain calls handle_pending on all its commands."""
    cmd1 = MockCommand()
    cmd2 = MockCommand()
    chain = CommandChain(cmd1, cmd2)
    env = Environment()
    chain.handle_pending(env)
    assert cmd1.handle_pending_called
    assert cmd2.handle_pending_called

def test_command_chain_integration():
    """Tests a more realistic scenario with command consumption."""
    class ConsumingMockCommand(Command):
        def __init__(self, texts_to_handle: list[str]):
            self.texts_to_handle = texts_to_handle

        def handle(self, text: str, env: Environment) -> bool:
            return text in self.texts_to_handle

    cmd1 = ConsumingMockCommand(["cmd1", "cmd2"])
    cmd2 = ConsumingMockCommand(["cmd3"])

    chain = CommandChain(cmd1, cmd2)
    env = Environment()
    queue = env[CommandQueueEnv]
    queue.add(["cmd1", "cmd2", "cmd3", "cmd4"])

    chain.handle_pending(env)

    # cmd1 should consume cmd1 and cmd2.
    # cmd2 should consume cmd3.
    # cmd4 should remain.
    assert queue.get() == ["cmd4"]
