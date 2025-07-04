from functools import cache
from llobot.knowledge.subsets import KnowledgeSubset
import llobot.knowledge.subsets

@cache
def suffix() -> KnowledgeSubset:
    return llobot.knowledge.subsets.suffix('.java')

@cache
def package_info() -> KnowledgeSubset:
    return llobot.knowledge.subsets.filename('package-info.java')

@cache
def module_info() -> KnowledgeSubset:
    return llobot.knowledge.subsets.filename('module-info.java')

@cache
def special() -> KnowledgeSubset:
    return package_info() | module_info()

@cache
def regular() -> KnowledgeSubset:
    return suffix() - special()

@cache
def tests() -> KnowledgeSubset:
    return llobot.knowledge.subsets.glob('**/*Test.java', '**/*Tests.java') | llobot.knowledge.subsets.glob('**/src/test/**')

@cache
def benchmarks() -> KnowledgeSubset:
    return llobot.knowledge.subsets.glob('**/*Benchmark.java')

@cache
def resources() -> KnowledgeSubset:
    return llobot.knowledge.subsets.glob('**/src/*/resources/**')

@cache
def pom() -> KnowledgeSubset:
    return llobot.knowledge.subsets.filename('pom.xml')

@cache
def properties() -> KnowledgeSubset:
    return llobot.knowledge.subsets.suffix('.properties')

@cache
def build() -> KnowledgeSubset:
    return llobot.knowledge.subsets.directory('target')

@cache
def whitelist() -> KnowledgeSubset:
    return suffix() | pom() | properties()

@cache
def blacklist() -> KnowledgeSubset:
    return build()

@cache
def ancillary() -> KnowledgeSubset:
    return special() | tests() | resources() | pom() | properties()

__all__ = [
    'suffix',
    'package_info',
    'module_info',
    'special',
    'regular',
    'tests',
    'benchmarks',
    'resources',
    'pom',
    'properties',
    'build',
    'whitelist',
    'blacklist',
    'ancillary',
]

