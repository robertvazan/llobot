import pytest
from llobot.environments import Environment
from llobot.commands.unrecognized import UnrecognizedCommand

def test_unrecognized_command_handle_raises():
    """Tests that UnrecognizedCommand.handle raises ValueError."""
    cmd = UnrecognizedCommand()
    env = Environment()
    with pytest.raises(ValueError, match="Unrecognized: some command"):
        cmd.handle("some command", env)
