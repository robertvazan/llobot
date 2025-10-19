from pathlib import Path
from llobot.commands.retrievals import flush_retrieval_commands
from llobot.environments import Environment
from llobot.environments.knowledge import KnowledgeEnv
from llobot.environments.retrievals import RetrievalsEnv
from llobot.environments.context import ContextEnv
from llobot.knowledge import Knowledge
from llobot.knowledge.ranking import KnowledgeRanking
from llobot.knowledge.ranking.lexicographical import rank_lexicographically
from llobot.knowledge.ranking.rankers import KnowledgeRanker
from llobot.chats.monolithic import monolithic_chat


class ReversedLexicographicalRanker(KnowledgeRanker):
    def rank(self, knowledge: Knowledge) -> KnowledgeRanking:
        return rank_lexicographically(knowledge).reversed()


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
    flush_retrieval_commands(env)
    assert not env[ContextEnv].populated
    assert not env[RetrievalsEnv].get()

def test_one_retrieval():
    env = create_env()
    env[RetrievalsEnv].add(Path('a.txt'))
    flush_retrieval_commands(env)
    context = env[ContextEnv]
    assert context.populated
    assert 'File: a.txt' in monolithic_chat(context.build())
    assert 'content a' in monolithic_chat(context.build())
    assert not env[RetrievalsEnv].get()

def test_multiple_retrievals():
    env = create_env()
    env[RetrievalsEnv].add(Path('b.txt'))
    env[RetrievalsEnv].add(Path('a.txt'))
    flush_retrieval_commands(env)
    context = env[ContextEnv]
    monolithic = monolithic_chat(context.build())
    assert 'File: a.txt' in monolithic
    assert 'content a' in monolithic
    assert 'File: b.txt' in monolithic
    assert 'content b' in monolithic
    assert monolithic.find('File: a.txt') < monolithic.find('File: b.txt')
    assert not env[RetrievalsEnv].get()

def test_ranking_order():
    env = create_env()
    env[RetrievalsEnv].add(Path('a.txt'))
    env[RetrievalsEnv].add(Path('c.txt'))
    env[RetrievalsEnv].add(Path('b.txt'))
    flush_retrieval_commands(env, ranker=ReversedLexicographicalRanker())
    context = env[ContextEnv]
    monolithic = monolithic_chat(context.build())
    pos_a = monolithic.find('File: a.txt')
    pos_b = monolithic.find('File: b.txt')
    pos_c = monolithic.find('File: c.txt')
    assert pos_c < pos_b < pos_a
    assert not env[RetrievalsEnv].get()

def test_duplicate_retrieval_prevention():
    env = create_env()
    env[RetrievalsEnv].add(Path('a.txt'))
    flush_retrieval_commands(env)
    context = env[ContextEnv]
    initial_messages_count = len(context.build())
    env[RetrievalsEnv].add(Path('a.txt'))
    flush_retrieval_commands(env)
    assert len(context.build()) == initial_messages_count
    assert not env[RetrievalsEnv].get()
