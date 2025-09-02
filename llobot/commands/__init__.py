"""
Command execution framework for roles.

This package defines the `Command` class, which serves as a base for
implementing commands that can be included in a user's request. Roles can
use these commands to manipulate their execution environment.

Submodules
----------

chains
    Command chains.
mentions
    Parser for @command mentions in chat messages.
projects
    Command to select a project.
retrievals
    Command to retrieve a document.
cutoffs
    Command to set knowledge cutoff.
"""
from __future__ import annotations
from llobot.chats import ChatBranch, ChatIntent
from llobot.environments import Environment
from llobot.environments.sessions import SessionEnv

class Command:
    """
    Base class for commands that can be executed by a role.

    Commands are responsible for parsing a command string and manipulating
    the environment accordingly.
    """
    def handle(self, text: str, env: Environment) -> bool:
        """
        Handles a command if it is recognized.

        Subclasses should override this method to implement command-specific
        logic. The method should return `True` if the command was handled,
        and `False` otherwise.

        Args:
            text: The unparsed command string.
            env: The environment to manipulate.

        Returns:
            `True` if the command was handled, `False` otherwise.
        """
        return False

    def handle_or_fail(self, text: str, env: Environment):
        """
        Executes the command or raises an exception if it is not recognized.

        Args:
            text: The unparsed command string.
            env: The environment to manipulate.

        Raises:
            ValueError: If the command is not handled.
        """
        if not self.handle(text, env):
            raise ValueError(f'Unrecognized: {text}')

    def handle_all(self, texts: list[str], env: Environment):
        """
        Executes a list of commands.

        Args:
            texts: A list of unparsed command strings.
            env: The environment to manipulate.

        Raises:
            ValueError: If any command is not handled.
        """
        for text in texts:
            self.handle_or_fail(text, env)

    def handle_chat(self, chat: ChatBranch, env: Environment):
        """
        Parses and executes commands from all messages in a chat.

        Session recording is enabled for the last message in the chat.
        This method also reorders prompt-session message pairs to session-prompt pairs.

        Args:
            chat: The chat branch to process.
            env: The environment to manipulate.
        """
        import llobot.commands.mentions

        messages = chat.messages
        # Reorder prompt-session pairs.
        reordered = []
        i = 0
        while i < len(messages):
            if (i + 1 < len(messages) and
                    messages[i].intent == ChatIntent.PROMPT and
                    messages[i+1].intent == ChatIntent.SESSION):
                reordered.append(messages[i+1])
                reordered.append(messages[i])
                i += 2
            else:
                reordered.append(messages[i])
                i += 1

        for i, message in enumerate(reordered):
            if i == len(reordered) - 1:
                env[SessionEnv].record()
            commands = llobot.commands.mentions.parse(message)
            self.handle_all(commands, env)

__all__ = [
    'Command',
]
