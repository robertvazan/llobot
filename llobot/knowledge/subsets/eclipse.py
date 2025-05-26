from functools import cache
from llobot.knowledge.subsets import KnowledgeSubset
import llobot.knowledge.subsets

@cache
def workspace() -> KnowledgeSubset:
    return llobot.knowledge.subsets.directory('.settings', '.metadata')

@cache
def blacklist() -> KnowledgeSubset:
    return workspace()

__all__ = [
    'workspace',
    'blacklist',
]

