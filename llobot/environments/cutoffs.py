"""
Knowledge cutoff environment component.
"""
from __future__ import annotations
from datetime import datetime
from llobot.time import current_time, format_time
from llobot.environments import EnvBase
from llobot.environments.projects import ProjectEnv
from llobot.environments.session_messages import SessionMessageEnv

class CutoffEnv(EnvBase):
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

    def get(self) -> datetime:
        """
        Gets the currently configured cutoff.

        If no cutoff was configured, it is generated based on the current time.
        If a project is selected, its knowledge is refreshed before generating the cutoff.
        The generated cutoff is recorded in the session.

        Returns:
            The configured or generated knowledge cutoff.
        """
        if self._cutoff is None:
            project = self.env[ProjectEnv].get()
            if project:
                project.refresh()
            self._cutoff = current_time()
            self.env[SessionMessageEnv].append(f"Knowledge cutoff: @{format_time(self._cutoff)}")
        return self._cutoff

__all__ = [
    'CutoffEnv',
]
