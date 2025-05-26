from functools import cache
from llobot.knowledge.subsets import KnowledgeSubset
import llobot.knowledge.subsets

@cache
def suffix() -> KnowledgeSubset:
    return llobot.knowledge.subsets.suffix('.toml')

@cache
def whitelist() -> KnowledgeSubset:
    return suffix()

__all__ = [
    'suffix',
    'whitelist',
]

