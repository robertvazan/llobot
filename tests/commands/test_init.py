import pytest
from llobot.environments import Environment
from llobot.environments.sessions import SessionEnv
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

def test_command_handle_chat():
    """Tests Command.handle_chat parsing and execution flow."""
    handled_commands = []
    class TestCommand(Command):
        def handle(self, text: str, env: Environment) -> bool:
            if text.startswith("cmd"):
                handled_commands.append(text)
                env[SessionEnv].append(f"Handled {text}")
                return True
            return False

    cmd = TestCommand()
    env = Environment()
    chat = ChatBranch([
        ChatMessage(ChatIntent.PROMPT, "first message with @cmd1"),
        ChatMessage(ChatIntent.RESPONSE, "second message with @cmd2 and @cmd3")
    ])

    cmd.handle_chat(chat, env)

    assert handled_commands == ["cmd1", "cmd2", "cmd3"]
    session_env = env[SessionEnv]
    assert session_env.recording()
    assert session_env.content() == "Handled cmd2\n\nHandled cmd3"
    assert session_env.message().content == "Handled cmd2\n\nHandled cmd3"

def test_command_handle_chat_reorder():
    """Tests reordering of prompt-session pairs in handle_chat."""
    handled_commands_from_messages = []

    class MockCommand(Command):
        def handle_all(self, texts: list[str], env: Environment):
            handled_commands_from_messages.append(texts)

    cmd = MockCommand()
    env = Environment()
    chat = ChatBranch([
        ChatMessage(ChatIntent.PROMPT, "msg @p1"),
        ChatMessage(ChatIntent.SESSION, "msg @s1"),
        ChatMessage(ChatIntent.RESPONSE, "msg @r1"),
        ChatMessage(ChatIntent.PROMPT, "msg @p2"),
        ChatMessage(ChatIntent.SESSION, "msg @s2"),
    ])

    cmd.handle_chat(chat, env)

    assert handled_commands_from_messages == [['s1'], [], ['p1'], ['r1'], ['s2'], [], ['p2']]
