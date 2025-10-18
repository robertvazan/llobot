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
    the `ProjectLibrary` configured in `ProjectEnv`. If one or more projects
    are found, they are added to the `ProjectEnv`.
    """
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
        project_env = env[ProjectEnv]
        found = project_env.add(text)
        return bool(found)

__all__ = [
    'ProjectCommand',
]
