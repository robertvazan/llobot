from functools import cache
from llobot.knowledge.subsets import KnowledgeSubset
import llobot.knowledge.subsets

@cache
def suffix() -> KnowledgeSubset:
    return llobot.knowledge.subsets.suffix('.py')

@cache
def requirements() -> KnowledgeSubset:
    return llobot.knowledge.subsets.filename('requirements.txt')

@cache
def whitelist() -> KnowledgeSubset:
    return suffix() | requirements()

@cache
def ancillary() -> KnowledgeSubset:
    return requirements()

__all__ = [
    'suffix',
    'requirements',
    'whitelist',
    'ancillary',
]

