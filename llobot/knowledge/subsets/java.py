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
    return llobot.knowledge.subsets.glob('**/*Test.java')

@cache
def benchmarks() -> KnowledgeSubset:
    return llobot.knowledge.subsets.glob('**/*Benchmark.java')

@cache
def main_tree() -> KnowledgeSubset:
    return llobot.knowledge.subsets.glob('**/src/main/**')

@cache
def test_tree() -> KnowledgeSubset:
    return llobot.knowledge.subsets.glob('**/src/test/**')

@cache
def resources() -> KnowledgeSubset:
    return llobot.knowledge.subsets.glob('**/src/*/resources/**')

@cache
def test_resources() -> KnowledgeSubset:
    return llobot.knowledge.subsets.glob('**/src/test/resources/**')

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
def boilerplate() -> KnowledgeSubset:
    return test_resources()

@cache
def unimportant() -> KnowledgeSubset:
    return boilerplate() | special() | resources() | pom() | properties()

@cache
def relevant() -> KnowledgeSubset:
    return regular() - tests() - test_tree() - benchmarks()

__all__ = [
    'suffix',
    'package_info',
    'module_info',
    'special',
    'regular',
    'tests',
    'benchmarks',
    'main_tree',
    'test_tree',
    'resources',
    'test_resources',
    'pom',
    'properties',
    'build',
    'whitelist',
    'blacklist',
    'boilerplate',
    'unimportant',
    'relevant',
]

