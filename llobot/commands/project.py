"""
Command to select a project.
"""
from __future__ import annotations
from collections import defaultdict
from pathlib import Path
from typing import Iterable
from llobot.commands import Command
from llobot.environments import Environment
from llobot.environments.projects import ProjectEnv
from llobot.projects import Project

class ProjectCommand(Command):
    """
    A command that selects one or more projects to be used as a knowledge base.

    The command handler expects the command text to be a zone identifier. If
    one or more projects are associated with that zone, they are added to the
    `ProjectEnv` of the environment.
    """
    _projects: list[Project]
    _zone_map: dict[str, list[Project]]

    def __init__(self, projects: Iterable[Project] = ()):
        """
        Initializes the ProjectCommand.

        Args:
            projects: A list of available projects.
        """
        self._projects = list(projects)
        self._zone_map = defaultdict(list)
        for p in self._projects:
            for zone in p.zones:
                self._zone_map[str(zone)].append(p)

    def handle(self, text: str, env: Environment) -> bool:
        """
        Handles the project selection command.

        If `text` is a zone that matches one or more known projects, those
        projects are added to the environment's `ProjectEnv`.

        Args:
            text: The command string, expected to be a zone identifier.
            env: The environment to manipulate.

        Returns:
            `True` if any project was selected, `False` otherwise.
        """
        if text in self._zone_map:
            for project in self._zone_map[text]:
                env[ProjectEnv].add(project)
            return True
        return False

__all__ = [
    'ProjectCommand',
]
