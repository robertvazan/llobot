from pathlib import PurePosixPath
from unittest.mock import MagicMock
from llobot.crammers.knowledge.ranked import RankedKnowledgeCrammer
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.knowledge import KnowledgeEnv
from llobot.environments.projects import ProjectEnv
from llobot.knowledge import Knowledge
from llobot.knowledge.ranking import KnowledgeRanking
from llobot.knowledge.ranking.lexicographical import LexicographicalRanker
from llobot.knowledge.subsets.empty import EmptySubset

def setup_env(knowledge: Knowledge, budget: int) -> Environment:
    """Sets up an environment with mocked project and knowledge."""
    env = Environment()

    # Setup context
    builder = env[ContextEnv].builder
    builder.budget = budget

    # Setup project to return provided knowledge
    mock_project = MagicMock()
    mock_project.read_all.return_value = knowledge
    # Inject mock project into ProjectEnv cache
    env[ProjectEnv].__dict__['union'] = mock_project

    return env

def test_cram_all_fit():
    """Tests cramming when all documents fit."""
    k = Knowledge({
        PurePosixPath("a.txt"): "aaa",
        PurePosixPath("b.txt"): "bbb",
    })
    crammer = RankedKnowledgeCrammer(
        ranker=LexicographicalRanker(),
        blacklist=EmptySubset()
    )
    env = setup_env(k, 1000)

    crammer.cram(env)

    # Check ContextEnv
    chat = env[ContextEnv].build()
    assert any("File: ~/a.txt" in msg.content for msg in chat)
    assert any("File: ~/b.txt" in msg.content for msg in chat)

    # Check KnowledgeEnv
    assert "a.txt" in env[KnowledgeEnv]
    assert "b.txt" in env[KnowledgeEnv]

def test_cram_some_fit():
    """Tests cramming when only some documents fit."""
    # Use long content to make budget calculations predictable
    k = Knowledge({
        PurePosixPath("a.txt"): "a" * 500,
        PurePosixPath("b.txt"): "b" * 500,
        PurePosixPath("c.txt"): "c" * 500,
    })
    # Lexicographical ranker will order them a, b, c
    crammer = RankedKnowledgeCrammer(
        ranker=LexicographicalRanker(),
        blacklist=EmptySubset()
    )
    # Budget for roughly two files
    env = setup_env(k, 1200)

    crammer.cram(env)

    # Check ContextEnv
    chat = env[ContextEnv].build()
    assert any("File: ~/a.txt" in msg.content for msg in chat)
    assert any("File: ~/b.txt" in msg.content for msg in chat)
    assert not any("File: ~/c.txt" in msg.content for msg in chat)

    # Check KnowledgeEnv
    assert "a.txt" in env[KnowledgeEnv]
    assert "b.txt" in env[KnowledgeEnv]
    assert "c.txt" not in env[KnowledgeEnv]

def test_cram_refinement():
    """Tests the iterative refinement phase of cramming."""
    k = Knowledge({
        PurePosixPath("a.txt"): "a" * 500,
        PurePosixPath("b.txt"): "b" * 500,
    })
    # Lexicographical ranker will order them a, b
    crammer = RankedKnowledgeCrammer(
        ranker=LexicographicalRanker(),
        blacklist=EmptySubset()
    )
    # Budget allows raw content, but not with formatting overhead.
    env = setup_env(k, 1050)

    crammer.cram(env)

    # Check ContextEnv
    chat = env[ContextEnv].build()
    assert any("File: ~/a.txt" in msg.content for msg in chat)
    assert not any("File: ~/b.txt" in msg.content for msg in chat)

    # Check KnowledgeEnv
    assert "a.txt" in env[KnowledgeEnv]
    assert "b.txt" not in env[KnowledgeEnv]

def test_cram_with_blacklist():
    """Tests that blacklisted documents are not included."""
    k = Knowledge({
        PurePosixPath("a.txt"): "aaa",
        PurePosixPath("b.txt"): "bbb",
    })
    crammer = RankedKnowledgeCrammer(
        ranker=LexicographicalRanker(),
        blacklist=KnowledgeRanking([PurePosixPath("a.txt")]) # blacklist a.txt
    )
    env = setup_env(k, 1000)

    crammer.cram(env)

    # Check ContextEnv
    chat = env[ContextEnv].build()
    assert any("File: ~/b.txt" in msg.content for msg in chat)
    assert not any("File: ~/a.txt" in msg.content for msg in chat)

    # Check KnowledgeEnv
    assert "b.txt" in env[KnowledgeEnv]
    assert "a.txt" not in env[KnowledgeEnv]
