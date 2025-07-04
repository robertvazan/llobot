from functools import cache
from llobot.knowledge.subsets import KnowledgeSubset
import llobot.knowledge.subsets

@cache
def suffix() -> KnowledgeSubset:
    return llobot.knowledge.subsets.suffix('.rs')

@cache
def cargo() -> KnowledgeSubset:
    return llobot.knowledge.subsets.filename('Cargo.toml')

@cache
def tests() -> KnowledgeSubset:
    return suffix() & llobot.knowledge.subsets.directory('tests')

@cache
def build() -> KnowledgeSubset:
    return llobot.knowledge.subsets.directory('target')

@cache
def whitelist() -> KnowledgeSubset:
    return suffix() | cargo()

@cache
def blacklist() -> KnowledgeSubset:
    return build()

@cache
def ancillary() -> KnowledgeSubset:
    return cargo() | tests()

__all__ = [
    'suffix',
    'cargo',
    'tests',
    'build',
    'whitelist',
    'blacklist',
    'ancillary',
]

