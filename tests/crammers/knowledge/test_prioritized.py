from pathlib import Path
from llobot.chats.builders import ChatBuilder
from llobot.crammers.knowledge.prioritized import PrioritizedKnowledgeCrammer
from llobot.knowledge import Knowledge
from llobot.knowledge.ranking.lexicographical import LexicographicalRanker
from llobot.knowledge.scores.constant import ConstantScorer
from llobot.knowledge.scores.pagerank import PageRankScorer
from llobot.knowledge.scores.relevance import NegativeRelevanceScorer
from llobot.knowledge.subsets.empty import EmptySubset

def test_cram_all_fit():
    """Tests cramming when all documents fit."""
    k = Knowledge({
        Path("a.txt"): "aaa",
        Path("b.txt"): "bbb",
    })
    crammer = PrioritizedKnowledgeCrammer(
        relevance_scorer=ConstantScorer(),
        graph_scorer=PageRankScorer(),
        ranker=LexicographicalRanker(),
        blacklist=EmptySubset()
    )
    builder = ChatBuilder()
    builder.budget = 1000

    added = crammer.cram(builder, k)
    assert added == k.keys()
    chat_content = builder.build().monolithic()
    assert "File: a.txt" in chat_content
    assert "File: b.txt" in chat_content

def test_cram_some_fit():
    """Tests cramming when only some documents fit."""
    k = Knowledge({
        Path("a.txt"): "a" * 50,
        Path("b.txt"): "b" * 50,
    })
    crammer = PrioritizedKnowledgeCrammer(
        relevance_scorer=NegativeRelevanceScorer(),
        graph_scorer=PageRankScorer(),
        ranker=LexicographicalRanker(),
        blacklist=EmptySubset()
    )
    builder = ChatBuilder()
    # Budget for one file listing, but not two
    builder.budget = 150

    added = crammer.cram(builder, k)
    assert len(added) == 1
    # Lexicographical ranker, constant scores -> b.txt is last and removed
    assert Path("a.txt") in added
    assert Path("b.txt") not in added
