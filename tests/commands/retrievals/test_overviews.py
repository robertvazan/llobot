from pathlib import PurePosixPath
from llobot.commands.retrievals.overviews import assume_overview_retrieval_commands
from llobot.environments import Environment
from llobot.environments.knowledge import KnowledgeEnv
from llobot.environments.retrievals import RetrievalsEnv
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.subsets.parsing import parse_pattern

OVERVIEWS = parse_pattern('README.md', '__init__.py')
KNOWLEDGE = Knowledge({
    PurePosixPath('README.md'): 'root readme',
    PurePosixPath('a/__init__.py'): 'a init',
    PurePosixPath('a/README.md'): 'a readme',
    PurePosixPath('a/b/doc.txt'): 'not an overview',
    PurePosixPath('a/b/file.txt'): 'some file',
    PurePosixPath('a/b/__init__.py'): 'a/b init',
    PurePosixPath('c/file.txt'): 'another file'
})

def create_env() -> Environment:
    env = Environment()
    env[KnowledgeEnv].set(KNOWLEDGE)
    return env

def test_no_retrievals():
    env = create_env()
    assume_overview_retrieval_commands(env, overviews=OVERVIEWS)
    assert not env[RetrievalsEnv].get()

def test_retrieval_in_subdir():
    env = create_env()
    env[RetrievalsEnv].add(PurePosixPath('a/b/file.txt'))
    assume_overview_retrieval_commands(env, overviews=OVERVIEWS)
    assert env[RetrievalsEnv].get() == KnowledgeIndex([
        PurePosixPath('a/b/file.txt'),
        PurePosixPath('README.md'),
        PurePosixPath('a/__init__.py'),
        PurePosixPath('a/README.md'),
        PurePosixPath('a/b/__init__.py'),
    ])

def test_retrieval_in_root():
    env = create_env()
    knowledge = KNOWLEDGE | Knowledge({PurePosixPath('root.txt'): 'i am root'})
    env[KnowledgeEnv].set(knowledge)
    env[RetrievalsEnv].add(PurePosixPath('root.txt'))
    assume_overview_retrieval_commands(env, overviews=OVERVIEWS)
    assert env[RetrievalsEnv].get() == KnowledgeIndex([
        PurePosixPath('root.txt'),
        PurePosixPath('README.md'),
    ])

def test_multiple_retrievals():
    env = create_env()
    env[RetrievalsEnv].add(PurePosixPath('a/b/file.txt'))
    env[RetrievalsEnv].add(PurePosixPath('c/file.txt'))
    assume_overview_retrieval_commands(env, overviews=OVERVIEWS)
    assert env[RetrievalsEnv].get() == KnowledgeIndex([
        PurePosixPath('a/b/file.txt'),
        PurePosixPath('c/file.txt'),
        PurePosixPath('README.md'),
        PurePosixPath('a/__init__.py'),
        PurePosixPath('a/README.md'),
        PurePosixPath('a/b/__init__.py'),
    ])

def test_retrieved_is_overview():
    env = create_env()
    env[RetrievalsEnv].add(PurePosixPath('a/README.md'))
    assume_overview_retrieval_commands(env, overviews=OVERVIEWS)
    assert env[RetrievalsEnv].get() == KnowledgeIndex([
        PurePosixPath('a/README.md'),
        PurePosixPath('README.md'),
        PurePosixPath('a/__init__.py'),
    ])
