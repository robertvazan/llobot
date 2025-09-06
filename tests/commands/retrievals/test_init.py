from pathlib import Path
from llobot.commands.retrievals import RetrievalStep
from llobot.environments import Environment
from llobot.environments.knowledge import KnowledgeEnv
from llobot.environments.retrievals import RetrievalsEnv
from llobot.environments.context import ContextEnv
from llobot.knowledge import Knowledge
from llobot.formats.knowledge import standard_knowledge_format

KNOWLEDGE_FORMAT = standard_knowledge_format()
KNOWLEDGE = Knowledge({
    Path('a.txt'): 'content a',
    Path('b.txt'): 'content b',
    Path('c.txt'): 'content c',
})

def create_env() -> Environment:
    env = Environment()
    env[KnowledgeEnv].set(KNOWLEDGE)
    return env

def test_no_retrievals():
    env = create_env()
    step = RetrievalStep(KNOWLEDGE_FORMAT)
    step.process(env)
    assert not env[ContextEnv].messages
    assert not env[RetrievalsEnv].get()

def test_one_retrieval():
    env = create_env()
    step = RetrievalStep(KNOWLEDGE_FORMAT)
    env[RetrievalsEnv].add(Path('a.txt'))
    step.process(env)
    context = env[ContextEnv]
    assert len(context.messages) > 0
    assert 'File: a.txt' in context.build().monolithic()
    assert 'content a' in context.build().monolithic()
    assert not env[RetrievalsEnv].get()

def test_multiple_retrievals():
    env = create_env()
    step = RetrievalStep(KNOWLEDGE_FORMAT)
    env[RetrievalsEnv].add(Path('a.txt'))
    step.process(env)
    env[RetrievalsEnv].add(Path('b.txt'))
    step.process(env)
    context = env[ContextEnv]
    monolithic = context.build().monolithic()
    assert 'File: a.txt' in monolithic
    assert 'content a' in monolithic
    assert 'File: b.txt' in monolithic
    assert 'content b' in monolithic
    assert not env[RetrievalsEnv].get()

def test_duplicate_retrieval_prevention():
    env = create_env()
    step = RetrievalStep(KNOWLEDGE_FORMAT)
    env[RetrievalsEnv].add(Path('a.txt'))
    step.process(env)
    context = env[ContextEnv]
    initial_messages_count = len(context.messages)
    env[RetrievalsEnv].add(Path('a.txt'))
    step.process(env)
    assert len(context.messages) == initial_messages_count
    assert not env[RetrievalsEnv].get()
