import pytest
from llobot.environments import Environment
from llobot.commands.unrecognized import handle_unrecognized_command

def test_handle_unrecognized_command_raises():
    """Tests that handle_unrecognized_command raises ValueError."""
    env = Environment()
    with pytest.raises(ValueError, match="Unrecognized: some command"):
        handle_unrecognized_command("some command", env)
