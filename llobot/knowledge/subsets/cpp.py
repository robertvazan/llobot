from functools import cache
from llobot.knowledge.subsets import KnowledgeSubset
import llobot.knowledge.subsets

SUFFIXES = ['.c', '.h', '.cpp', '.hpp', '.hh', '.hxx', '.cxx', '.cc']

@cache
def suffix() -> KnowledgeSubset:
    return llobot.knowledge.subsets.suffix(*SUFFIXES)

@cache
def whitelist() -> KnowledgeSubset:
    return suffix()

__all__ = [
    'SUFFIXES',
    'suffix',
    'whitelist',
]

