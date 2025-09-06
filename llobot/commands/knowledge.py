"""
Command to load project knowledge.
"""
from __future__ import annotations
from llobot.commands import Command
from llobot.environments import Environment
from llobot.environments.cutoffs import CutoffEnv
from llobot.environments.knowledge import KnowledgeEnv
from llobot.environments.projects import ProjectEnv

class LoadKnowledgeCommand(Command):
    """
    A command that loads the knowledge for the selected project at the
    selected cutoff time.
    """
    def process(self, env: Environment):
        """
        Loads knowledge from the project in `ProjectEnv` at the time specified
        in `CutoffEnv` and stores it in `KnowledgeEnv`. If no project is set,
        it does nothing.

        Args:
            env: The environment.
        """
        project = env[ProjectEnv].get()
        if project:
            cutoff = env[CutoffEnv].get()
            knowledge = project.knowledge(cutoff)
            env[KnowledgeEnv].set(knowledge)

__all__ = [
    'LoadKnowledgeCommand',
]
