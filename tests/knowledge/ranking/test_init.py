from pathlib import PurePosixPath

from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.ranking import (
    KnowledgeRanking,
    coerce_ranking,
    standard_ranking,
)

KNOWLEDGE_INDEX = KnowledgeIndex([
    PurePosixPath("a/b/c.txt"),
    PurePosixPath("a/README.md"),
    PurePosixPath("main.py"),
    PurePosixPath("README.md"),
    PurePosixPath("a/b/__init__.py"),
])

KNOWLEDGE = Knowledge({path: "" for path in KNOWLEDGE_INDEX})


def test_coerce_ranking_from_ranking():
    ranking = KnowledgeRanking([PurePosixPath("b"), PurePosixPath("a")])
    assert coerce_ranking(ranking) is ranking


def test_coerce_ranking_from_index():
    index = KnowledgeIndex([PurePosixPath("b"), PurePosixPath("a")])
    ranking = coerce_ranking(index)
    assert ranking == KnowledgeRanking([PurePosixPath("a"), PurePosixPath("b")])


def test_coerce_ranking_from_knowledge():
    knowledge = Knowledge({PurePosixPath("b"): "", PurePosixPath("a"): ""})
    ranking = coerce_ranking(knowledge)
    assert ranking == KnowledgeRanking([PurePosixPath("a"), PurePosixPath("b")])


def test_standard_ranking_from_index():
    ranking = standard_ranking(KNOWLEDGE_INDEX)
    assert ranking == KnowledgeRanking(
        [
            PurePosixPath("README.md"),
            PurePosixPath("main.py"),
            PurePosixPath("a/README.md"),
            PurePosixPath("a/b/__init__.py"),
            PurePosixPath("a/b/c.txt"),
        ]
    )


def test_standard_ranking_from_knowledge():
    ranking = standard_ranking(KNOWLEDGE)
    assert ranking == KnowledgeRanking(
        [
            PurePosixPath("README.md"),
            PurePosixPath("main.py"),
            PurePosixPath("a/README.md"),
            PurePosixPath("a/b/__init__.py"),
            PurePosixPath("a/b/c.txt"),
        ]
    )
