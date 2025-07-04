from functools import cache
from llobot.knowledge.subsets import KnowledgeSubset
import llobot.knowledge.subsets

@cache
def readme() -> KnowledgeSubset:
    return llobot.knowledge.subsets.filename('README', 'README.md', 'README.txt')

@cache
def copyright() -> KnowledgeSubset:
    return llobot.knowledge.subsets.filename('COPYRIGHT', 'COPYRIGHT.md', 'COPYRIGHT.txt')

@cache
def contributors() -> KnowledgeSubset:
    return llobot.knowledge.subsets.filename('CONTRIBUTORS', 'CONTRIBUTORS.md', 'CONTRIBUTORS.txt')

@cache
def authors() -> KnowledgeSubset:
    return llobot.knowledge.subsets.filename('AUTHORS', 'AUTHORS.md', 'AUTHORS.txt')

@cache
def acknowledgements() -> KnowledgeSubset:
    return llobot.knowledge.subsets.filename('ACKNOWLEDGMENTS', 'ACKNOWLEDGMENTS.md', 'ACKNOWLEDGMENTS.txt')

@cache
def license() -> KnowledgeSubset:
    return llobot.knowledge.subsets.filename('LICENSE', 'LICENSE.md', 'LICENSE.txt')

@cache
def code_of_conduct() -> KnowledgeSubset:
    return llobot.knowledge.subsets.filename('CODE_OF_CONDUCT', 'CODE_OF_CONDUCT.md', 'CODE_OF_CONDUCT.txt')

@cache
def legal() -> KnowledgeSubset:
    return copyright() | contributors() | authors() | acknowledgements() | license() | code_of_conduct()

@cache
def changelog() -> KnowledgeSubset:
    return llobot.knowledge.subsets.filename('CHANGELOG', 'CHANGELOG.md', 'CHANGELOG.txt')

@cache
def support() -> KnowledgeSubset:
    return llobot.knowledge.subsets.filename('SUPPORT', 'SUPPORT.md', 'SUPPORT.txt')

@cache
def security() -> KnowledgeSubset:
    return llobot.knowledge.subsets.filename('SECURITY', 'SECURITY.md', 'SECURITY.txt')

@cache
def contributing() -> KnowledgeSubset:
    return llobot.knowledge.subsets.filename('CONTRIBUTING', 'CONTRIBUTING.md', 'CONTRIBUTING.txt')

@cache
def boilerplate() -> KnowledgeSubset:
    return legal() | changelog() | support() | security() | contributing()

@cache
def texts() -> KnowledgeSubset:
    return boilerplate() | readme()

@cache
def whitelist() -> KnowledgeSubset:
    return texts()

__all__ = [
    'readme',
    'copyright',
    'contributors',
    'authors',
    'acknowledgements',
    'license',
    'code_of_conduct',
    'legal',
    'changelog',
    'suport',
    'security',
    'contributing',
    'boilerplate',
    'texts',
    'whitelist',
]

