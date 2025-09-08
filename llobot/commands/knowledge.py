"""
Step to load project knowledge.
"""
from __future__ import annotations
from llobot.commands import Step
from llobot.environments import Environment
from llobot.environments.cutoff import CutoffEnv
from llobot.environments.knowledge import KnowledgeEnv
from llobot.environments.projects import ProjectEnv
from llobot.knowledge.archives import KnowledgeArchive

class ProjectKnowledgeStep(Step):
    """
    A step that loads the knowledge for the selected project at the
    selected cutoff time from a knowledge archive.
    """
    _archive: KnowledgeArchive

    def __init__(self, archive: KnowledgeArchive):
        """
        Initializes the step.

        Args:
            archive: The archive to load knowledge from.
        """
        self._archive = archive

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
            knowledge = self._archive.last(project.name, cutoff)
            env[KnowledgeEnv].set(knowledge)

__all__ = [
    'ProjectKnowledgeStep',
]
