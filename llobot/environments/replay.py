"""
Replay/record state of the environment.
"""
from __future__ import annotations
from llobot.environments import EnvBase

class ReplayEnv(EnvBase):
    """
    An environment component that indicates whether the environment is in replay or recording state.
    """
    _recording: bool = False

    def start_recording(self):
        """
        Switches the environment into recording state.
        """
        self._recording = True

    def recording(self) -> bool:
        """
        Checks whether the environment is in recording state.
        """
        return self._recording

    def replaying(self) -> bool:
        """
        Checks whether the environment is in replay state.
        """
        return not self._recording

__all__ = [
    'ReplayEnv',
]
