from functools import cache
from llobot.knowledge.subsets import KnowledgeSubset
import llobot.knowledge.subsets

@cache
def directory() -> KnowledgeSubset:
    return llobot.knowledge.subsets.directory('.vscode')

@cache
def blacklist() -> KnowledgeSubset:
    return directory()

__all__ = [
    'directory',
    'blacklist',
]

