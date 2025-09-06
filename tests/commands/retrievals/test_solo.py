from pathlib import Path
from llobot.commands.retrievals.solo import SoloRetrievalCommand
from llobot.environments import Environment
from llobot.environments.knowledge import KnowledgeEnv
from llobot.environments.retrievals import RetrievalsEnv
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex

COMMAND = SoloRetrievalCommand()
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
    assert not COMMAND.handle('e.txt', env)
    assert not env[RetrievalsEnv].get()

def test_multiple_matches():
    env = create_env()
    assert not COMMAND.handle('a/*.txt', env)
    assert not env[RetrievalsEnv].get()

def test_not_a_path():
    env = create_env()
    assert not COMMAND.handle('hello world', env)
    assert not env[RetrievalsEnv].get()

def test_exact_match():
    env = create_env()
    assert COMMAND.handle('d.txt', env)
    assert env[RetrievalsEnv].get() == KnowledgeIndex([Path('d.txt')])
