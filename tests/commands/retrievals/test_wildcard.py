from pathlib import Path
from llobot.commands.retrievals.wildcard import WildcardRetrievalCommand
from llobot.environments import Environment
from llobot.environments.knowledge import KnowledgeEnv
from llobot.environments.retrievals import RetrievalsEnv
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex

COMMAND = WildcardRetrievalCommand()
KNOWLEDGE = Knowledge({
    Path('a/b.txt'): 'content',
    Path('a/c.txt'): 'another',
    Path('d.txt'): 'root file',
    Path('x/y/z.txt'): 'deep file'
})

def create_env() -> Environment:
    env = Environment()
    env[KnowledgeEnv].set(KNOWLEDGE)
    return env

def test_no_match():
    env = create_env()
    assert not COMMAND.handle('e/*.txt', env)
    assert not env[RetrievalsEnv].get()

def test_no_wildcard():
    env = create_env()
    assert not COMMAND.handle('a/b.txt', env)
    assert not env[RetrievalsEnv].get()

def test_no_slash():
    env = create_env()
    assert not COMMAND.handle('*.txt', env)
    assert not env[RetrievalsEnv].get()

def test_single_match():
    env = create_env()
    assert COMMAND.handle('x/y/*.txt', env)
    assert env[RetrievalsEnv].get() == KnowledgeIndex([Path('x/y/z.txt')])

def test_multiple_matches():
    env = create_env()
    assert COMMAND.handle('a/*.txt', env)
    assert env[RetrievalsEnv].get() == KnowledgeIndex([Path('a/b.txt'), Path('a/c.txt')])

def test_absolute_path_match():
    env = create_env()
    assert COMMAND.handle('/a/*.txt', env)
    assert env[RetrievalsEnv].get() == KnowledgeIndex([Path('a/b.txt'), Path('a/c.txt')])

def test_deep_match():
    env = create_env()
    assert COMMAND.handle('**/*.txt', env)
    assert env[RetrievalsEnv].get() == KNOWLEDGE.keys()

def test_invalid_characters():
    env = create_env()
    assert not COMMAND.handle('a/*.txt$', env)
    assert not env[RetrievalsEnv].get()
