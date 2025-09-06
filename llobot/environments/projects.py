"""
Project selection environment component.
"""
from __future__ import annotations
from llobot.projects import Project

class ProjectEnv:
    """
    An environment component that holds the currently selected project.
    """
    _project: Project | None = None

    def set(self, project: Project):
        """
        Sets the project for the environment.

        Args:
            project: The project to set.

        Raises:
            ValueError: If a different project is already set.
        """
        if self._project is not None and self._project is not project:
            raise ValueError(f"Project already set to {self._project.name}, cannot change to {project.name}")
        self._project = project

    def get(self) -> Project | None:
        """
        Gets the currently selected project.

        Returns:
            The selected project, or None if no project is selected.
        """
        return self._project

__all__ = [
    'ProjectEnv',
]
