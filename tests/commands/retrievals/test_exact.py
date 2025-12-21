from pathlib import PurePosixPath
from llobot.commands.retrievals.exact import handle_exact_retrieval_command
from llobot.environments import Environment
from llobot.environments.knowledge import KnowledgeEnv
from llobot.environments.retrievals import RetrievalsEnv
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex

KNOWLEDGE = Knowledge({
    PurePosixPath('a/b.txt'): 'content',
    PurePosixPath('a/c.txt'): 'another',
    PurePosixPath('d.txt'): 'root file',
})

def create_env() -> Environment:
    env = Environment()
    env[KnowledgeEnv].set(KNOWLEDGE)
    return env

def test_no_match():
    env = create_env()
    assert not handle_exact_retrieval_command('e.txt', env)
    assert not env[RetrievalsEnv].get()

def test_multiple_matches():
    knowledge = Knowledge({
        PurePosixPath('a/b.txt'): 'content',
        PurePosixPath('x/b.txt'): 'another content',
    })
    env = Environment()
    env[KnowledgeEnv].set(knowledge)
    assert handle_exact_retrieval_command('b.txt', env)
    assert env[RetrievalsEnv].get() == knowledge.keys()

def test_not_a_path():
    env = create_env()
    assert not handle_exact_retrieval_command('hello world', env)
    assert not env[RetrievalsEnv].get()

def test_invalid_characters():
    env = create_env()
    assert not handle_exact_retrieval_command('d.txt$', env)
    assert not env[RetrievalsEnv].get()

def test_exact_match():
    env = create_env()
    assert handle_exact_retrieval_command('d.txt', env)
    assert env[RetrievalsEnv].get() == KnowledgeIndex([PurePosixPath('d.txt')])

def test_absolute_path_match():
    env = create_env()
    assert handle_exact_retrieval_command('/a/b.txt', env)
    assert env[RetrievalsEnv].get() == KnowledgeIndex([PurePosixPath('a/b.txt')])

def test_wildcard_is_ignored():
    env = create_env()
    assert not handle_exact_retrieval_command('a/*.txt', env)
    assert not env[RetrievalsEnv].get()
