from pathlib import Path
from llobot.commands.retrievals.overviews import assume_overview_retrieval_commands
from llobot.environments import Environment
from llobot.environments.knowledge import KnowledgeEnv
from llobot.environments.retrievals import RetrievalsEnv
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.subsets.parsing import parse_pattern

OVERVIEWS = parse_pattern('README.md', '__init__.py')
KNOWLEDGE = Knowledge({
    Path('README.md'): 'root readme',
    Path('a/__init__.py'): 'a init',
    Path('a/README.md'): 'a readme',
    Path('a/b/doc.txt'): 'not an overview',
    Path('a/b/file.txt'): 'some file',
    Path('a/b/__init__.py'): 'a/b init',
    Path('c/file.txt'): 'another file'
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
    env[RetrievalsEnv].add(Path('a/b/file.txt'))
    assume_overview_retrieval_commands(env, overviews=OVERVIEWS)
    assert env[RetrievalsEnv].get() == KnowledgeIndex([
        Path('a/b/file.txt'),
        Path('README.md'),
        Path('a/__init__.py'),
        Path('a/README.md'),
        Path('a/b/__init__.py'),
    ])

def test_retrieval_in_root():
    env = create_env()
    knowledge = KNOWLEDGE | Knowledge({Path('root.txt'): 'i am root'})
    env[KnowledgeEnv].set(knowledge)
    env[RetrievalsEnv].add(Path('root.txt'))
    assume_overview_retrieval_commands(env, overviews=OVERVIEWS)
    assert env[RetrievalsEnv].get() == KnowledgeIndex([
        Path('root.txt'),
        Path('README.md'),
    ])

def test_multiple_retrievals():
    env = create_env()
    env[RetrievalsEnv].add(Path('a/b/file.txt'))
    env[RetrievalsEnv].add(Path('c/file.txt'))
    assume_overview_retrieval_commands(env, overviews=OVERVIEWS)
    assert env[RetrievalsEnv].get() == KnowledgeIndex([
        Path('a/b/file.txt'),
        Path('c/file.txt'),
        Path('README.md'),
        Path('a/__init__.py'),
        Path('a/README.md'),
        Path('a/b/__init__.py'),
    ])

def test_retrieved_is_overview():
    env = create_env()
    env[RetrievalsEnv].add(Path('a/README.md'))
    assume_overview_retrieval_commands(env, overviews=OVERVIEWS)
    assert env[RetrievalsEnv].get() == KnowledgeIndex([
        Path('a/README.md'),
        Path('README.md'),
        Path('a/__init__.py'),
    ])
