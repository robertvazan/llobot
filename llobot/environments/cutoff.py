"""
Knowledge cutoff environment component.
"""
from __future__ import annotations
from datetime import datetime
from llobot.utils.time import format_time

class CutoffEnv:
    """
    An environment component that holds the knowledge cutoff timestamp.
    """
    _cutoff: datetime | None = None

    def set(self, cutoff: datetime):
        """
        Sets the knowledge cutoff for the environment.

        It is okay to set the same cutoff multiple times.

        Args:
            cutoff: The knowledge cutoff to set.

        Raises:
            ValueError: If a different cutoff is already set.
        """
        if self._cutoff is not None and self._cutoff != cutoff:
            raise ValueError(f"Cutoff already set to {format_time(self._cutoff)}, cannot change to {format_time(cutoff)}")
        self._cutoff = cutoff

    def get(self) -> datetime | None:
        """
        Gets the currently configured cutoff.

        Returns:
            The configured knowledge cutoff, or None if not set.
        """
        return self._cutoff

    def clear(self):
        """
        Clears the configured cutoff.
        """
        self._cutoff = None

__all__ = [
    'CutoffEnv',
]
