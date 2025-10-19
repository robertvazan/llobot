"""
Function to load project knowledge.
"""
from __future__ import annotations
from llobot.environments import Environment
from llobot.environments.knowledge import KnowledgeEnv
from llobot.environments.projects import ProjectEnv

def populate_knowledge_env(env: Environment):
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
    'populate_knowledge_env',
]
