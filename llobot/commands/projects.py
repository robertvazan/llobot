"""
Command to select a project.
"""
from __future__ import annotations
from llobot.commands import Command
from llobot.environments import Environment
from llobot.environments.projects import ProjectEnv
from llobot.projects import Project

class ProjectCommand(Command):
    """
    A command that selects a project to be used as a knowledge base.

    The command handler expects the command text to be the name of a project.
    If a matching project is found, it is set in the `ProjectEnv` of the
    environment.
    """
    _projects: dict[str, Project]

    def __init__(self, projects: list[Project] | None = None):
        """
        Initializes the ProjectCommand.

        Args:
            projects: A list of available projects.
        """
        self._projects = {p.name: p for p in projects} if projects else {}

    def handle(self, text: str, env: Environment) -> bool:
        """
        Handles the project selection command.

        If `text` matches a known project name, the project is set in the
        environment's `ProjectEnv`.

        Args:
            text: The command string, expected to be a project name.
            env: The environment to manipulate.

        Returns:
            `True` if a project was selected, `False` otherwise.
        """
        if text in self._projects:
            project = self._projects[text]
            env[ProjectEnv].set(project)
            return True
        return False

__all__ = [
    'ProjectCommand',
]
