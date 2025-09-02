"""
Project selection environment component.
"""
from __future__ import annotations
from llobot.environments import EnvBase
from llobot.projects import Project

class ProjectEnv(EnvBase):
    """
    An environment component that holds the currently selected project.

    Once the project is retrieved via `get()`, it cannot be changed anymore.
    """
    _project: Project | None = None
    _frozen: bool = False

    def set(self, project: Project):
        """
        Sets the project for the environment.

        Args:
            project: The project to set.

        Raises:
            ValueError: If a different project is already set or if the project
                        selection has been frozen by calling `get()`.
        """
        if self._frozen:
            raise ValueError("Project selection is frozen and cannot be changed.")
        if self._project is not None and self._project is not project:
            raise ValueError(f"Project already set to {self._project.name}, cannot change to {project.name}")
        self._project = project

    def get(self) -> Project | None:
        """
        Gets the currently selected project and freezes the selection.

        Returns:
            The selected project, or None if no project is selected.
        """
        self._frozen = True
        return self._project

__all__ = [
    'ProjectEnv',
]
