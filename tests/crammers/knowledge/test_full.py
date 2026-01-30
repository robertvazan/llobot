from pathlib import PurePosixPath
from unittest.mock import MagicMock
from llobot.crammers.knowledge.full import FullKnowledgeCrammer
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.knowledge import KnowledgeEnv
from llobot.environments.projects import ProjectEnv
from llobot.knowledge import Knowledge
from llobot.knowledge.ranking.lexicographical import LexicographicalRanker
from llobot.knowledge.subsets import coerce_subset
from llobot.knowledge.subsets.empty import EmptySubset

def setup_env(knowledge: Knowledge) -> Environment:
    """Sets up an environment with mocked project and knowledge."""
    env = Environment()

    # Setup project to return provided knowledge
    mock_project = MagicMock()
    mock_project.read_all.return_value = knowledge
    # Inject mock project into ProjectEnv cache
    env[ProjectEnv].__dict__['union'] = mock_project

    return env

def test_cram_all():
    """Tests cramming all documents."""
    k = Knowledge({
        PurePosixPath("a.txt"): "aaa",
        PurePosixPath("b.txt"): "bbb",
    })
    crammer = FullKnowledgeCrammer(
        ranker=LexicographicalRanker(),
        blacklist=EmptySubset(),
    )
    env = setup_env(k)

    crammer.cram(env)

    # Check ContextEnv
    chat = env[ContextEnv].build()
    assert any("File: ~/a.txt" in msg.content for msg in chat)
    assert any("File: ~/b.txt" in msg.content for msg in chat)

    # Check KnowledgeEnv
    assert "a.txt" in env[KnowledgeEnv]
    assert "b.txt" in env[KnowledgeEnv]

def test_cram_with_blacklist():
    """Tests that blacklisted documents are not included."""
    k = Knowledge({
        PurePosixPath("a.txt"): "aaa",
        PurePosixPath("b.txt"): "bbb",
    })
    crammer = FullKnowledgeCrammer(
        ranker=LexicographicalRanker(),
        blacklist=coerce_subset(PurePosixPath("a.txt")), # blacklist a.txt
    )
    env = setup_env(k)

    crammer.cram(env)

    # Check ContextEnv
    chat = env[ContextEnv].build()
    assert any("File: ~/b.txt" in msg.content for msg in chat)
    assert not any("File: ~/a.txt" in msg.content for msg in chat)

    # Check KnowledgeEnv
    assert "b.txt" in env[KnowledgeEnv]
    assert "a.txt" not in env[KnowledgeEnv]

def test_cram_skips_existing():
    """Tests that files already in KnowledgeEnv are skipped."""
    k = Knowledge({
        PurePosixPath("a.txt"): "aaa",
        PurePosixPath("b.txt"): "bbb",
    })
    crammer = FullKnowledgeCrammer(
        ranker=LexicographicalRanker(),
        blacklist=EmptySubset(),
    )
    env = setup_env(k)
    # Pre-populate KnowledgeEnv
    env[KnowledgeEnv].add(PurePosixPath("a.txt"), "aaa")

    crammer.cram(env)

    # Check ContextEnv
    chat = env[ContextEnv].build()
    # a.txt should NOT be added again
    assert not any("File: ~/a.txt" in msg.content for msg in chat)
    # b.txt SHOULD be added
    assert any("File: ~/b.txt" in msg.content for msg in chat)

    # Check KnowledgeEnv
    assert "a.txt" in env[KnowledgeEnv]
    assert "b.txt" in env[KnowledgeEnv]

def test_cram_order():
    """Tests that documents are added in the ranked order."""
    k = Knowledge({
        PurePosixPath("b.txt"): "content b",
        PurePosixPath("a.txt"): "content a",
    })
    # LexicographicalRanker sorts to [a.txt, b.txt]
    crammer = FullKnowledgeCrammer(
        ranker=LexicographicalRanker(),
        blacklist=EmptySubset(),
    )
    env = setup_env(k)

    crammer.cram(env)

    chat = env[ContextEnv].build()
    full_text = "\n".join(msg.content for msg in chat)

    idx_a = full_text.find("File: ~/a.txt")
    idx_b = full_text.find("File: ~/b.txt")

    assert idx_a != -1
    assert idx_b != -1
    assert idx_a < idx_b

def test_cram_huge_content():
    """Tests that crammer adds content regardless of size/budget."""
    # Create content that would definitely exceed default budgets of RankedKnowledgeCrammer (50k)
    huge_content = "x" * 100_000
    k = Knowledge({
        PurePosixPath("large.txt"): huge_content,
        PurePosixPath("another.txt"): "small",
    })
    crammer = FullKnowledgeCrammer(
        ranker=LexicographicalRanker(),
        blacklist=EmptySubset(),
    )
    env = setup_env(k)

    crammer.cram(env)

    chat = env[ContextEnv].build()
    full_text = "\n".join(msg.content for msg in chat)

    assert "File: ~/large.txt" in full_text
    assert "File: ~/another.txt" in full_text
    assert len(full_text) >= 100_000
