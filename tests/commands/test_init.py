import pytest
from llobot.environments import Environment
from llobot.commands import Command

def test_command_handle_default():
    """Tests that Command.handle returns False by default."""
    cmd = Command()
    env = Environment()
    assert not cmd.handle("some command", env)

def test_command_call_unhandled():
    """Tests that Command.__call__ raises ValueError for unhandled commands."""
    cmd = Command()
    env = Environment()
    with pytest.raises(ValueError, match="Unrecognized command: some command"):
        cmd("some command", env)

def test_command_call_handled():
    """Tests that Command.__call__ does not raise for handled commands."""
    class HandledCommand(Command):
        def handle(self, text: str, env: Environment) -> bool:
            return True

    cmd = HandledCommand()
    env = Environment()
    cmd("some command", env)  # Should not raise
