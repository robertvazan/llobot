import os
from pathlib import PurePosixPath, Path
from llobot.commands.retrievals import flush_retrieval_commands
from llobot.environments import Environment
from llobot.environments.projects import ProjectEnv
from llobot.environments.retrievals import RetrievalsEnv
from llobot.environments.context import ContextEnv
from llobot.knowledge import Knowledge
from llobot.knowledge.ranking import KnowledgeRanking
from llobot.knowledge.ranking.lexicographical import rank_lexicographically
from llobot.knowledge.ranking.rankers import KnowledgeRanker
from llobot.projects.directory import DirectoryProject
from llobot.projects.library.predefined import PredefinedProjectLibrary


class ReversedLexicographicalRanker(KnowledgeRanker):
    def rank(self, knowledge: Knowledge) -> KnowledgeRanking:
        return rank_lexicographically(knowledge).reversed()


KNOWLEDGE = {
    PurePosixPath('a.txt'): 'content a',
    PurePosixPath('b.txt'): 'content b',
    PurePosixPath('c.txt'): 'content c',
}

def create_env(tmp_path: Path) -> Environment:
    env = Environment()
    root = tmp_path / 'project'
    root.mkdir()
    for path, content in KNOWLEDGE.items():
        full_path = root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)

    project = DirectoryProject(root, prefix=PurePosixPath('project'))
    library = PredefinedProjectLibrary({'project': project})

    project_env = env[ProjectEnv]
    project_env.configure(library)
    project_env.add('project')
    return env

def test_no_retrievals(tmp_path):
    env = create_env(tmp_path)
    flush_retrieval_commands(env)
    assert not env[ContextEnv].populated
    assert not env[RetrievalsEnv].get()

def test_one_retrieval(tmp_path):
    env = create_env(tmp_path)
    env[RetrievalsEnv].add(PurePosixPath('project/a.txt'))
    flush_retrieval_commands(env)
    context = env[ContextEnv]
    assert context.populated
    context_chat = context.build()
    assert any('File: ~/project/a.txt' in msg.content for msg in context_chat)
    assert any('content a' in msg.content for msg in context_chat)
    assert not env[RetrievalsEnv].get()

def test_multiple_retrievals(tmp_path):
    env = create_env(tmp_path)
    env[RetrievalsEnv].add(PurePosixPath('project/b.txt'))
    env[RetrievalsEnv].add(PurePosixPath('project/a.txt'))
    flush_retrieval_commands(env)
    context = env[ContextEnv]
    context_chat = context.build()
    assert any('File: ~/project/a.txt' in msg.content for msg in context_chat)
    assert any('content a' in msg.content for msg in context_chat)
    assert any('File: ~/project/b.txt' in msg.content for msg in context_chat)
    assert any('content b' in msg.content for msg in context_chat)

    # Cannot easily check order without monolithic string.
    # We rely on ranker test for order.
    # The default ranker is lexicographical.
    assert not env[RetrievalsEnv].get()

def test_ranking_order(tmp_path):
    env = create_env(tmp_path)
    env[RetrievalsEnv].add(PurePosixPath('project/a.txt'))
    env[RetrievalsEnv].add(PurePosixPath('project/c.txt'))
    env[RetrievalsEnv].add(PurePosixPath('project/b.txt'))
    flush_retrieval_commands(env, ranker=ReversedLexicographicalRanker())
    context = env[ContextEnv]
    context_chat = context.build()

    # The ranker should order files c, b, a.
    # The files are rendered into a single message.
    contents = [msg.content for msg in context_chat if 'File:' in msg.content]
    assert len(contents) == 1
    content = contents[0]
    c_pos = content.find('File: ~/project/c.txt')
    b_pos = content.find('File: ~/project/b.txt')
    a_pos = content.find('File: ~/project/a.txt')
    assert -1 < c_pos < b_pos < a_pos
    assert not env[RetrievalsEnv].get()

def test_duplicate_retrieval_prevention(tmp_path):
    env = create_env(tmp_path)
    env[RetrievalsEnv].add(PurePosixPath('project/a.txt'))
    flush_retrieval_commands(env)
    context = env[ContextEnv]
    initial_messages_count = len(context.build())
    env[RetrievalsEnv].add(PurePosixPath('project/a.txt'))
    flush_retrieval_commands(env)
    assert len(context.build()) == initial_messages_count
    assert not env[RetrievalsEnv].get()

def test_filter_missing_files(tmp_path):
    """
    Tests that files that are not readable (e.g. missing) are filtered out.
    """
    env = create_env(tmp_path)
    # Simulate a missing file by deleting it after environment creation
    missing_file = tmp_path / 'project' / 'a.txt'
    os.remove(missing_file)

    env[RetrievalsEnv].add(PurePosixPath('project/a.txt'))
    flush_retrieval_commands(env)

    context_chat = env[ContextEnv].build()
    # Should not include a.txt since it was deleted
    assert not any('File: ~/project/a.txt' in msg.content for msg in context_chat)
    assert not env[RetrievalsEnv].get()
