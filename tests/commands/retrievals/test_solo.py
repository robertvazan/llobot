from pathlib import Path
from llobot.commands.retrievals.solo import handle_solo_retrieval_command
from llobot.environments import Environment
from llobot.environments.knowledge import KnowledgeEnv
from llobot.environments.retrievals import RetrievalsEnv
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex

KNOWLEDGE = Knowledge({
    Path('a/b.txt'): 'content',
    Path('a/c.txt'): 'another',
    Path('d.txt'): 'root file',
})

def create_env() -> Environment:
    env = Environment()
    env[KnowledgeEnv].set(KNOWLEDGE)
    return env

def test_no_match():
    env = create_env()
    assert not handle_solo_retrieval_command('e.txt', env)
    assert not env[RetrievalsEnv].get()

def test_multiple_matches():
    knowledge = Knowledge({
        Path('a/b.txt'): 'content',
        Path('x/b.txt'): 'another content',
    })
    env = Environment()
    env[KnowledgeEnv].set(knowledge)
    assert not handle_solo_retrieval_command('b.txt', env)
    assert not env[RetrievalsEnv].get()

def test_not_a_path():
    env = create_env()
    assert not handle_solo_retrieval_command('hello world', env)
    assert not env[RetrievalsEnv].get()

def test_invalid_characters():
    env = create_env()
    assert not handle_solo_retrieval_command('d.txt$', env)
    assert not env[RetrievalsEnv].get()

def test_exact_match():
    env = create_env()
    assert handle_solo_retrieval_command('d.txt', env)
    assert env[RetrievalsEnv].get() == KnowledgeIndex([Path('d.txt')])

def test_absolute_path_match():
    env = create_env()
    assert handle_solo_retrieval_command('/a/b.txt', env)
    assert env[RetrievalsEnv].get() == KnowledgeIndex([Path('a/b.txt')])

def test_wildcard_is_ignored():
    env = create_env()
    assert not handle_solo_retrieval_command('a/*.txt', env)
    assert not env[RetrievalsEnv].get()
