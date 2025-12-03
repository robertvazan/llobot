"""
Tool execution environment.
"""
from __future__ import annotations
from llobot.environments.persistent import PersistentEnv

class ToolEnv:
    """
    Environment component for accumulating tool execution logs.
    """
    _log: list[str]

    def __init__(self):
        self._log = []

    def log(self, message: str):
        """
        Appends a message to the tool execution log.

        Args:
            message: The message to log.
        """
        self._log.append(message)

    def flush_log(self) -> str:
        """
        Returns the accumulated log and clears the buffer.

        Returns:
            The joined log messages separated by newlines.
        """
        result = '\n'.join(self._log)
        self._log.clear()
        return result

__all__ = [
    'ToolEnv',
]
