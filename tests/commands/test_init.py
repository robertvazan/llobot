import pytest
from llobot.environments import Environment
from llobot.environments.replay import ReplayEnv
from llobot.environments.session_messages import SessionMessageEnv
from llobot.commands import Command
from llobot.chats.branches import ChatBranch
from llobot.chats.messages import ChatMessage
from llobot.chats.intents import ChatIntent

def test_command_handle_default():
    """Tests that Command.handle returns False by default."""
    cmd = Command()
    env = Environment()
    assert not cmd.handle("some command", env)

def test_command_handle_or_fail_unhandled():
    """Tests that Command.handle_or_fail raises ValueError for unhandled commands."""
    cmd = Command()
    env = Environment()
    with pytest.raises(ValueError, match="Unrecognized: some command"):
        cmd.handle_or_fail("some command", env)

def test_command_handle_or_fail_handled():
    """Tests that Command.handle_or_fail does not raise for handled commands."""
    class HandledCommand(Command):
        def handle(self, text: str, env: Environment) -> bool:
            return True

    cmd = HandledCommand()
    env = Environment()
    cmd.handle_or_fail("some command", env)  # Should not raise

def test_command_handle_all():
    """Tests Command.handle_all with multiple commands."""
    handled_commands = []
    class RecordingCommand(Command):
        def handle(self, text: str, env: Environment) -> bool:
            handled_commands.append(text)
            return True

    cmd = RecordingCommand()
    env = Environment()
    cmd.handle_all(["cmd1", "cmd2"], env)
    assert handled_commands == ["cmd1", "cmd2"]
