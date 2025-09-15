from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.scores import KnowledgeScores
from llobot.knowledge.scores.directory import directory_max_scores, directory_sum_scores, directory_count_scores

knowledge = Knowledge({
    Path('a/b/c.txt'): 'C',
    Path('a/b/d.txt'): 'DD',
    Path('a/e.txt'): 'E',
    Path('f.txt'): 'F',
})

scores = KnowledgeScores({
    Path('a/b/c.txt'): 1.0,
    Path('a/b/d.txt'): 2.0,
    Path('a/e.txt'): 5.0,
})

def test_directory_max_scores():
    dir_scores = directory_max_scores(scores)
    assert dir_scores[Path('a/b')] == 2.0
    assert dir_scores[Path('a')] == 5.0
    assert Path('.') not in dir_scores
    assert Path('a/b/c.txt') not in dir_scores

def test_directory_max_scores_non_recursive():
    dir_scores = directory_max_scores(scores, recursive=False)
    assert dir_scores[Path('a/b')] == 2.0
    assert dir_scores[Path('a')] == 5.0
    assert Path('.') not in dir_scores

def test_directory_sum_scores():
    dir_scores = directory_sum_scores(scores)
    assert dir_scores[Path('a/b')] == 3.0
    assert dir_scores[Path('a')] == 8.0
    assert Path('.') not in dir_scores

def test_directory_sum_scores_non_recursive():
    dir_scores = directory_sum_scores(scores, recursive=False)
    assert dir_scores[Path('a/b')] == 3.0
    assert dir_scores[Path('a')] == 5.0
    assert Path('.') not in dir_scores

def test_directory_count_scores():
    dir_scores = directory_count_scores(knowledge)
    assert dir_scores[Path('a/b')] == 2
    assert dir_scores[Path('a')] == 3
    assert Path('.') not in dir_scores

def test_directory_count_scores_non_recursive():
    dir_scores = directory_count_scores(knowledge, recursive=False)
    assert dir_scores[Path('a/b')] == 2
    assert dir_scores[Path('a')] == 1
    assert Path('.') not in dir_scores
