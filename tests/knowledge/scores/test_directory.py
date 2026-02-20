from pathlib import PurePosixPath
from typing import Any, cast
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.scores import KnowledgeScores
from llobot.knowledge.scores.directory import directory_max_scores, directory_sum_scores, directory_count_scores

knowledge = Knowledge({
    PurePosixPath('a/b/c.txt'): 'C',
    PurePosixPath('a/b/d.txt'): 'DD',
    PurePosixPath('a/e.txt'): 'E',
    PurePosixPath('f.txt'): 'F',
})

scores = KnowledgeScores({
    PurePosixPath('a/b/c.txt'): 1.0,
    PurePosixPath('a/b/d.txt'): 2.0,
    PurePosixPath('a/e.txt'): 5.0,
})

def test_directory_max_scores():
    dir_scores = directory_max_scores(scores)
    assert dir_scores[PurePosixPath('a/b')] == 2.0
    assert dir_scores[PurePosixPath('a')] == 5.0
    assert PurePosixPath('.') not in dir_scores
    assert PurePosixPath('a/b/c.txt') not in dir_scores

def test_directory_max_scores_non_recursive():
    dir_scores = directory_max_scores(scores, recursive=False)
    assert dir_scores[PurePosixPath('a/b')] == 2.0
    assert dir_scores[PurePosixPath('a')] == 5.0
    assert PurePosixPath('.') not in dir_scores

def test_directory_sum_scores():
    dir_scores = directory_sum_scores(scores)
    assert dir_scores[PurePosixPath('a/b')] == 3.0
    assert dir_scores[PurePosixPath('a')] == 8.0
    assert PurePosixPath('.') not in dir_scores

def test_directory_sum_scores_non_recursive():
    dir_scores = directory_sum_scores(scores, recursive=False)
    assert dir_scores[PurePosixPath('a/b')] == 3.0
    assert dir_scores[PurePosixPath('a')] == 5.0
    assert PurePosixPath('.') not in dir_scores

def test_directory_count_scores():
    dir_scores = directory_count_scores(knowledge)
    assert dir_scores[PurePosixPath('a/b')] == 2
    assert dir_scores[PurePosixPath('a')] == 3
    assert PurePosixPath('.') not in dir_scores

def test_directory_count_scores_non_recursive():
    dir_scores = directory_count_scores(knowledge, recursive=False)
    assert dir_scores[PurePosixPath('a/b')] == 2
    assert dir_scores[PurePosixPath('a')] == 1
    assert PurePosixPath('.') not in dir_scores

def test_directory_count_scores_from_index():
    index = KnowledgeIndex([PurePosixPath('a/b.txt'), PurePosixPath('a/c.txt')])
    dir_scores = directory_count_scores(index)
    assert dir_scores[PurePosixPath('a')] == 2

def test_directory_count_scores_invalid_type():
    try:
        directory_count_scores(cast(Any, KnowledgeScores({PurePosixPath('a.txt'): 1.0})))
        assert False, "Should have raised TypeError"
    except TypeError:
        pass
