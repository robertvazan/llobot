from functools import cache
from llobot.knowledge.subsets import KnowledgeSubset
import llobot.knowledge.subsets

@cache
def repository() -> KnowledgeSubset:
    return llobot.knowledge.subsets.directory('.git')

@cache
def gitignore() -> KnowledgeSubset:
    return llobot.knowledge.subsets.filename('.gitignore')

@cache
def gitattributes() -> KnowledgeSubset:
    return llobot.knowledge.subsets.filename('.gitattributes')

@cache
def mailmap() -> KnowledgeSubset:
    return llobot.knowledge.subsets.filename('.mailmap')

@cache
def gitmodules() -> KnowledgeSubset:
    return llobot.knowledge.subsets.filename('.gitmodules')

@cache
def whitelist() -> KnowledgeSubset:
    return gitignore() | gitattributes() | mailmap() | gitmodules()

@cache
def blacklist() -> KnowledgeSubset:
    return repository()

@cache
def boilerplate() -> KnowledgeSubset:
    return whitelist()

__all__ = [
    'repository',
    'gitignore',
    'whitelist',
    'blacklist',
    'boilerplate',
]

