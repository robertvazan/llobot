import pytest
from llobot.environments import Environment
from llobot.commands import Command
from llobot.commands.chains import CommandChain

class MockCommand(Command):
    def __init__(self, handles_command: bool, text_to_handle: str = "test"):
        self.handles_command = handles_command
        self.text_to_handle = text_to_handle
        self.was_called = False

    def handle(self, text: str, env: Environment) -> bool:
        self.was_called = True
        if self.handles_command and text == self.text_to_handle:
            return True
        return False

def test_command_chain_empty():
    """Tests that an empty CommandChain handles nothing."""
    chain = CommandChain()
    env = Environment()
    assert not chain.handle("test", env)

def test_command_chain_no_handler():
    """Tests that CommandChain returns False when no command handles the text."""
    cmd1 = MockCommand(False)
    cmd2 = MockCommand(False)
    chain = CommandChain(cmd1, cmd2)
    env = Environment()
    assert not chain.handle("test", env)
    assert cmd1.was_called
    assert cmd2.was_called

def test_command_chain_first_handles():
    """Tests that CommandChain stops at the first handler."""
    cmd1 = MockCommand(True)
    cmd2 = MockCommand(True)
    chain = CommandChain(cmd1, cmd2)
    env = Environment()
    assert chain.handle("test", env)
    assert cmd1.was_called
    assert not cmd2.was_called

def test_command_chain_second_handles():
    """Tests that CommandChain continues until a handler is found."""
    cmd1 = MockCommand(False)
    cmd2 = MockCommand(True)
    chain = CommandChain(cmd1, cmd2)
    env = Environment()
    assert chain.handle("test", env)
    assert cmd1.was_called
    assert cmd2.was_called

def test_command_chain_call_unhandled():
    """Tests that CommandChain.__call__ raises when no command handles the text."""
    chain = CommandChain(MockCommand(False), MockCommand(False))
    env = Environment()
    with pytest.raises(ValueError, match="Unrecognized: test"):
        chain("test", env)

def test_command_chain_call_handled():
    """Tests that CommandChain.__call__ does not raise when a command handles the text."""
    chain = CommandChain(MockCommand(False), MockCommand(True))
    env = Environment()
    chain("test", env)  # Should not raise
