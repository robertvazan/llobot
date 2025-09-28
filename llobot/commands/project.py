"""
Command to select a project.
"""
from __future__ import annotations
from llobot.commands import Command
from llobot.environments import Environment
from llobot.environments.projects import ProjectEnv
from llobot.projects.library import ProjectLibrary

class ProjectCommand(Command):
    """
    A command that selects one or more projects to be used as a knowledge base.

    The command handler uses the command text as a key to look up projects in
    a `ProjectLibrary`. If one or more projects are found, they are added to the
    `ProjectEnv` of the environment.
    """
    _library: ProjectLibrary

    def __init__(self, library: ProjectLibrary):
        """
        Initializes the `ProjectCommand`.

        Args:
            library: A project library to look up projects from.
        """
        self._library = library

    def handle(self, text: str, env: Environment) -> bool:
        """
        Handles the project selection command.

        If `text` is a key that matches one or more projects in the library,
        those projects are added to the environment's `ProjectEnv`.

        Args:
            text: The command string, used as a key for project lookup.
            env: The environment to manipulate.

        Returns:
            `True` if any project was selected, `False` otherwise.
        """
        found = self._library.lookup(text)
        if found:
            for project in found:
                env[ProjectEnv].add(project)
            return True
        return False

__all__ = [
    'ProjectCommand',
]
