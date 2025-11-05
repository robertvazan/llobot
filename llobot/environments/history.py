"""
Session history management.
"""
from __future__ import annotations
from pathlib import Path
from llobot.environments import Environment
from llobot.environments.session import SessionEnv
from llobot.utils.fs import data_home
from llobot.utils.time import format_time
from llobot.utils.zones import Zoning, coerce_zoning


class SessionHistory:
    """
    Manages persistence of Environment states for sessions.

    The session ID is obtained from the provided Environment's SessionEnv.
    If the Environment has no session ID configured, save/load operations
    are no-ops.
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

        The session ID is read from env[SessionEnv]. If there is no session ID,
        this method does nothing.

        Args:
            env: The environment to save.
        """
        session_id = env[SessionEnv].get_id()
        if not session_id:
            return
        zone = Path(format_time(session_id))
        path = self._location.resolve(zone)
        env.save(path)

    def load(self, env: Environment):
        """
        Loads an environment state for the current session.

        The session ID is read from env[SessionEnv]. If the session does not
        exist or there is no session ID, the environment is not modified.

        Args:
            env: The environment to load into.
        """
        session_id = env[SessionEnv].get_id()
        if not session_id:
            return
        zone = Path(format_time(session_id))
        path = self._location.resolve(zone)
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
