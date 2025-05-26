from functools import cache
from llobot.knowledge.subsets import KnowledgeSubset
import llobot.knowledge.subsets

@cache
def directory() -> KnowledgeSubset:
    return llobot.knowledge.subsets.directory('.github')

@cache
def dependabot() -> KnowledgeSubset:
    return llobot.knowledge.subsets.glob('**/.github/dependabot.yml')

@cache
def workflows() -> KnowledgeSubset:
    return llobot.knowledge.subsets.glob('**/.github/workflows/*.yml')

@cache
def whitelist() -> KnowledgeSubset:
    return dependabot() | workflows()

@cache
def boilerplate() -> KnowledgeSubset:
    return directory()

__all__ = [
    'directory',
    'dependabot',
    'workflows',
    'whitelist',
    'boilerplate',
]

