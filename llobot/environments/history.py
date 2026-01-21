"""
Session history management.
"""
from __future__ import annotations
import shutil
from pathlib import Path, PurePosixPath
from llobot.environments import Environment
from llobot.environments.prompt import PromptEnv
from llobot.utils.fs import data_home
from llobot.utils.zones import Zoning, coerce_zoning


class SessionHistory:
    """
    Manages persistence of Environment states for sessions.

    The session ID is a hash of the full prompt thread.
    """
    _location: Zoning

    def __init__(self, location: Zoning | Path | str):
        """
        Initializes a new SessionHistory.

        Args:
            location: The root directory or zoning configuration for the history.
        """
        self._location = coerce_zoning(location)

    def save(self, env: Environment):
        """
        Saves an environment state for the current session.

        The session ID is read from env[PromptEnv].hash. If there is no session ID,
        this method does nothing. If a session with the same ID already exists,
        it is removed before saving.

        Args:
            env: The environment to save.
        """
        session_id = env[PromptEnv].hash
        if not session_id:
            return
        zone = PurePosixPath(session_id)
        path = self._location.resolve(zone)

        if path.exists():
            shutil.rmtree(path)

        env.save(path)

    def load(self, env: Environment):
        """
        Loads an environment state for the previous session.

        The session ID is read from env[PromptEnv].previous_hash.
        If previous_hash is None, it assumes a new session and does nothing.
        If previous_hash is set but no corresponding session file is found,
        it raises a FileNotFoundError.

        Args:
            env: The environment to load into.

        Raises:
            FileNotFoundError: If the previous session is missing.
        """
        previous_id = env[PromptEnv].previous_hash
        if not previous_id:
            return

        zone = PurePosixPath(previous_id)
        path = self._location.resolve(zone)

        if not path.exists():
            raise FileNotFoundError(f"Previous session {previous_id} not found.")

        env.load(path)


def standard_session_history() -> SessionHistory:
    """
    Creates a standard session history in the default data location.

    Returns:
        A SessionHistory instance.
    """
    return SessionHistory(data_home()/'llobot/sessions')


def coerce_session_history(what: SessionHistory | Zoning | Path | str) -> SessionHistory:
    """
    Coerces various types into a SessionHistory instance.

    If `what` is already a `SessionHistory`, it's returned as is.
    Otherwise, a new `SessionHistory` is created from `what`.

    Args:
        what: The object to coerce.

    Returns:
        A SessionHistory instance.
    """
    if isinstance(what, SessionHistory):
        return what
    else:
        return SessionHistory(what)

__all__ = [
    'SessionHistory',
    'standard_session_history',
    'coerce_session_history',
]
