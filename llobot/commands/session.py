"""
Command and steps to manage session state.
"""
from __future__ import annotations
from llobot.commands import Command, Step
from llobot.environments import Environment
from llobot.environments.history import SessionHistory
from llobot.environments.session import SessionEnv
from llobot.utils.time import format_time, try_parse_time

class SessionCommand(Command):
    """
    A command to set the session ID from a timestamp string.
    """
    def handle(self, text: str, env: Environment) -> bool:
        """
        Handles the command if the text is a valid timestamp.

        Args:
            text: The unparsed command string, expected to be a timestamp.
            env: The environment to manipulate.

        Returns:
            `True` if the command was handled, `False` otherwise.
        """
        session_id = try_parse_time(text)
        if session_id:
            env[SessionEnv].set_id(session_id)
            return True
        return False

class ImplicitSessionStep(Step):
    """
    A step that sets the session ID to the current time if it's not
    already set, and adds a session message with the ID.
    """
    def process(self, env: Environment):
        """
        If no session ID is set, this method generates one, sets it in the
        `SessionEnv`, and adds a session message indicating the new session ID.

        Args:
            env: The environment.
        """
        session_env = env[SessionEnv]
        if session_env.get_id() is None:
            from llobot.utils.time import current_time
            session_id = current_time()
            session_env.set_id(session_id)
            session_env.append(f"Session: @{format_time(session_id)}")

class SessionLoadStep(Step):
    """
    A step that loads the environment from the session history.
    """
    _history: SessionHistory

    def __init__(self, history: SessionHistory):
        """
        Initializes the step.

        Args:
            history: The session history to load the environment from.
        """
        self._history = history

    def process(self, env: Environment):
        """
        If a session ID is set in the `SessionEnv`, this method loads the
        environment state from the corresponding location in the session history.

        Args:
            env: The environment to load into.
        """
        session_id = env[SessionEnv].get_id()
        if session_id:
            self._history.load(session_id, env)

__all__ = [
    'SessionCommand',
    'ImplicitSessionStep',
    'SessionLoadStep',
]
