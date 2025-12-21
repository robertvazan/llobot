from pathlib import PurePosixPath
from llobot.commands.retrievals import flush_retrieval_commands
from llobot.environments import Environment
from llobot.environments.knowledge import KnowledgeEnv
from llobot.environments.retrievals import RetrievalsEnv
from llobot.environments.context import ContextEnv
from llobot.knowledge import Knowledge
from llobot.knowledge.ranking import KnowledgeRanking
from llobot.knowledge.ranking.lexicographical import rank_lexicographically
from llobot.knowledge.ranking.rankers import KnowledgeRanker


class ReversedLexicographicalRanker(KnowledgeRanker):
    def rank(self, knowledge: Knowledge) -> KnowledgeRanking:
        return rank_lexicographically(knowledge).reversed()


KNOWLEDGE = Knowledge({
    PurePosixPath('a.txt'): 'content a',
    PurePosixPath('b.txt'): 'content b',
    PurePosixPath('c.txt'): 'content c',
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
    env[RetrievalsEnv].add(PurePosixPath('a.txt'))
    flush_retrieval_commands(env)
    context = env[ContextEnv]
    assert context.populated
    context_chat = context.build()
    assert any('File: a.txt' in msg.content for msg in context_chat)
    assert any('content a' in msg.content for msg in context_chat)
    assert not env[RetrievalsEnv].get()

def test_multiple_retrievals():
    env = create_env()
    env[RetrievalsEnv].add(PurePosixPath('b.txt'))
    env[RetrievalsEnv].add(PurePosixPath('a.txt'))
    flush_retrieval_commands(env)
    context = env[ContextEnv]
    context_chat = context.build()
    assert any('File: a.txt' in msg.content for msg in context_chat)
    assert any('content a' in msg.content for msg in context_chat)
    assert any('File: b.txt' in msg.content for msg in context_chat)
    assert any('content b' in msg.content for msg in context_chat)

    # Cannot easily check order without monolithic string.
    # We rely on ranker test for order.
    # The default ranker is lexicographical.
    assert not env[RetrievalsEnv].get()

def test_ranking_order():
    env = create_env()
    env[RetrievalsEnv].add(PurePosixPath('a.txt'))
    env[RetrievalsEnv].add(PurePosixPath('c.txt'))
    env[RetrievalsEnv].add(PurePosixPath('b.txt'))
    flush_retrieval_commands(env, ranker=ReversedLexicographicalRanker())
    context = env[ContextEnv]
    context_chat = context.build()

    # The ranker should order files c, b, a.
    # The files are rendered into a single message.
    contents = [msg.content for msg in context_chat if 'File:' in msg.content]
    assert len(contents) == 1
    content = contents[0]
    c_pos = content.find('File: c.txt')
    b_pos = content.find('File: b.txt')
    a_pos = content.find('File: a.txt')
    assert -1 < c_pos < b_pos < a_pos
    assert not env[RetrievalsEnv].get()

def test_duplicate_retrieval_prevention():
    env = create_env()
    env[RetrievalsEnv].add(PurePosixPath('a.txt'))
    flush_retrieval_commands(env)
    context = env[ContextEnv]
    initial_messages_count = len(context.build())
    env[RetrievalsEnv].add(PurePosixPath('a.txt'))
    flush_retrieval_commands(env)
    assert len(context.build()) == initial_messages_count
    assert not env[RetrievalsEnv].get()
