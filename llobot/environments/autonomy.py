"""
Selected autonomy profile.
"""
from __future__ import annotations
from pathlib import Path
from llobot.environments.persistent import PersistentEnv
from llobot.roles.autonomy import Autonomy, NoAutonomy
from llobot.utils.fs import read_text, write_text

class AutonomyEnv(PersistentEnv):
    """
    An environment component that holds the currently selected autonomy profile.
    It can be persisted by saving the name of the selected profile.
    """
    _default: Autonomy
    _profiles: dict[str, Autonomy]
    _selected_name: str | None
    _selected_autonomy: Autonomy | None

    def __init__(self):
        self._default = NoAutonomy()
        self._profiles = {}
        self._selected_name = None
        self._selected_autonomy = None

    def configure(self, default: Autonomy, profiles: dict[str, Autonomy]):
        """
        Configures the default autonomy and available profiles.

        Args:
            default: The default autonomy to use if no profile is selected.
            profiles: A dictionary of available autonomy profiles.
        """
        self._default = default
        self._profiles = profiles

    def select(self, name: str) -> Autonomy | None:
        """
        Selects an autonomy profile by name.

        Args:
            name: The name of the profile to select.

        Returns:
            The selected Autonomy object if found, None otherwise.
        """
        if name in self._profiles:
            self._selected_name = name
            self._selected_autonomy = self._profiles[name]
            return self._selected_autonomy
        return None

    def get(self) -> Autonomy:
        """
        Gets the selected autonomy, or the default if none is selected.
        """
        if self._selected_autonomy:
            return self._selected_autonomy
        return self._default

    @property
    def selected_name(self) -> str | None:
        """
        Returns the name of the currently selected profile, or None if using default (or if default is not named).
        """
        return self._selected_name

    def save(self, directory: Path):
        """
        Saves the name of the selected profile to `autonomy.txt`.
        """
        if self._selected_name:
            write_text(directory / 'autonomy.txt', self._selected_name + '\n')

    def load(self, directory: Path):
        """
        Loads a profile name from `autonomy.txt`.

        Args:
            directory: The directory to load the state from.

        Raises:
            ValueError: If a profile name from `autonomy.txt` is not found in profiles.
        """
        self._selected_name = None
        self._selected_autonomy = None

        path = directory / 'autonomy.txt'
        if not path.exists():
            return

        name = read_text(path).strip()
        if name:
            if not self.select(name):
                raise ValueError(f"Autonomy profile '{name}' from autonomy.txt not found.")

__all__ = [
    'AutonomyEnv',
]
