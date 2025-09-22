from pathlib import Path

from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.ranking import (
    KnowledgeRanking,
    coerce_ranking,
    standard_ranking,
)

KNOWLEDGE_INDEX = KnowledgeIndex([
    Path("a/b/c.txt"),
    Path("a/README.md"),
    Path("main.py"),
    Path("README.md"),
    Path("a/b/__init__.py"),
])

KNOWLEDGE = Knowledge({path: "" for path in KNOWLEDGE_INDEX})


def test_coerce_ranking_from_ranking():
    ranking = KnowledgeRanking([Path("b"), Path("a")])
    assert coerce_ranking(ranking) is ranking


def test_coerce_ranking_from_index():
    index = KnowledgeIndex([Path("b"), Path("a")])
    ranking = coerce_ranking(index)
    assert ranking == KnowledgeRanking([Path("a"), Path("b")])


def test_coerce_ranking_from_knowledge():
    knowledge = Knowledge({Path("b"): "", Path("a"): ""})
    ranking = coerce_ranking(knowledge)
    assert ranking == KnowledgeRanking([Path("a"), Path("b")])


def test_standard_ranking_from_index():
    ranking = standard_ranking(KNOWLEDGE_INDEX)
    assert ranking == KnowledgeRanking(
        [
            Path("README.md"),
            Path("a/README.md"),
            Path("a/b/__init__.py"),
            Path("a/b/c.txt"),
            Path("main.py"),
        ]
    )


def test_standard_ranking_from_knowledge():
    ranking = standard_ranking(KNOWLEDGE)
    assert ranking == KnowledgeRanking(
        [
            Path("README.md"),
            Path("a/README.md"),
            Path("a/b/__init__.py"),
            Path("a/b/c.txt"),
            Path("main.py"),
        ]
    )
