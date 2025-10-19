"""
Step to load project knowledge.
"""
from __future__ import annotations
from llobot.commands import Step
from llobot.environments import Environment
from llobot.environments.knowledge import KnowledgeEnv
from llobot.environments.projects import ProjectEnv

class ProjectKnowledgeStep(Step):
    """
    A step that loads the knowledge for the selected projects.
    """
    def process(self, env: Environment):
        """
        Loads knowledge from the projects in `ProjectEnv` and stores the
        combined knowledge in `KnowledgeEnv`.

        Args:
            env: The environment.
        """
        union = env[ProjectEnv].union
        knowledge = union.read_all()
        env[KnowledgeEnv].set(knowledge)

__all__ = [
    'ProjectKnowledgeStep',
]
