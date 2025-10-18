from pathlib import Path
from llobot.chats.builder import ChatBuilder
from llobot.crammers.knowledge.ranked import RankedKnowledgeCrammer
from llobot.knowledge import Knowledge
from llobot.knowledge.ranking import KnowledgeRanking
from llobot.knowledge.ranking.lexicographical import LexicographicalRanker
from llobot.knowledge.subsets.empty import EmptySubset
from llobot.chats.monolithic import monolithic_chat

def test_cram_all_fit():
    """Tests cramming when all documents fit."""
    k = Knowledge({
        Path("a.txt"): "aaa",
        Path("b.txt"): "bbb",
    })
    crammer = RankedKnowledgeCrammer(
        ranker=LexicographicalRanker(),
        blacklist=EmptySubset()
    )
    builder = ChatBuilder()
    builder.budget = 1000

    added = crammer.cram(builder, k)
    assert added == k.keys()
    chat_content = monolithic_chat(builder.build())
    assert "File: a.txt" in chat_content
    assert "File: b.txt" in chat_content

def test_cram_some_fit():
    """Tests cramming when only some documents fit."""
    # Use long content to make budget calculations predictable
    k = Knowledge({
        Path("a.txt"): "a" * 500,
        Path("b.txt"): "b" * 500,
        Path("c.txt"): "c" * 500,
    })
    # Lexicographical ranker will order them a, b, c
    crammer = RankedKnowledgeCrammer(
        ranker=LexicographicalRanker(),
        blacklist=EmptySubset()
    )
    builder = ChatBuilder()
    # Budget for roughly two files, but not three.
    # A formatted file is about len(content) + 50 chars of overhead.
    # So 3 files would be ~1650. Budget for two is ~1100.
    builder.budget = 1200

    added = crammer.cram(builder, k)
    assert len(added) == 2
    assert Path("a.txt") in added
    assert Path("b.txt") in added
    assert Path("c.txt") not in added
    chat_content = monolithic_chat(builder.build())
    assert "File: a.txt" in chat_content
    assert "File: b.txt" in chat_content
    assert "File: c.txt" not in chat_content

def test_cram_refinement():
    """Tests the iterative refinement phase of cramming."""
    k = Knowledge({
        Path("a.txt"): "a" * 500,
        Path("b.txt"): "b" * 500,
    })
    # Lexicographical ranker will order them a, b
    crammer = RankedKnowledgeCrammer(
        ranker=LexicographicalRanker(),
        blacklist=EmptySubset()
    )
    builder = ChatBuilder()
    # Budget allows raw content, but not with formatting overhead.
    # Two files raw: 1000. Formatted: ~1100.
    builder.budget = 1050

    added = crammer.cram(builder, k)
    assert len(added) == 1
    assert Path("a.txt") in added
    assert Path("b.txt") not in added

def test_cram_with_blacklist():
    """Tests that blacklisted documents are not included."""
    k = Knowledge({
        Path("a.txt"): "aaa",
        Path("b.txt"): "bbb",
    })
    crammer = RankedKnowledgeCrammer(
        ranker=LexicographicalRanker(),
        blacklist=KnowledgeRanking([Path("a.txt")]) # blacklist a.txt
    )
    builder = ChatBuilder()
    builder.budget = 1000

    added = crammer.cram(builder, k)
    assert len(added) == 1
    assert Path("b.txt") in added
    assert Path("a.txt") not in added
