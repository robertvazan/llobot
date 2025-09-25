"""
Functions to aggregate scores by directory.
"""
from __future__ import annotations
from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex, KnowledgeIndexPrecursor
from llobot.knowledge.scores import KnowledgeScores
from llobot.knowledge.scores.constant import constant_scores

def directory_max_scores(scores: KnowledgeScores, *, recursive: bool = True) -> KnowledgeScores:
    """
    Assigns each directory the highest score among contained files.

    Args:
        scores: File scores to aggregate by directory.
        recursive: If True, includes files from subdirectories in scoring.

    Returns:
        Directory scores with maximum file score per directory.
    """
    directory_scores = {}

    for path, score in scores:
        if recursive:
            # Include all parent directories except root
            directories = [p for p in path.parents if p != Path('.')]
        else:
            # Include only immediate parent if it's not root
            parent = path.parent
            directories = [parent] if parent != Path('.') else []

        for directory in directories:
            current_max = directory_scores.get(directory, float('-inf'))
            directory_scores[directory] = max(current_max, score)

    return KnowledgeScores(directory_scores)

def directory_sum_scores(scores: KnowledgeScores, *, recursive: bool = True) -> KnowledgeScores:
    """
    Assigns each directory the sum of scores of contained files.

    Args:
        scores: File scores to aggregate by directory.
        recursive: If True, includes files from subdirectories in scoring.

    Returns:
        Directory scores with sum of file scores per directory.
    """
    directory_scores = {}

    for path, score in scores:
        if recursive:
            # Include all parent directories except root
            directories = [p for p in path.parents if p != Path('.')]
        else:
            # Include only immediate parent if it's not root
            parent = path.parent
            directories = [parent] if parent != Path('.') else []

        for directory in directories:
            directory_scores[directory] = directory_scores.get(directory, 0) + score

    return KnowledgeScores(directory_scores)

def directory_count_scores(keys: KnowledgeIndexPrecursor, *, recursive: bool = True) -> KnowledgeScores:
    """
    Assigns each directory the count of contained files.

    Args:
        keys: Files to count by directory. Can be a `KnowledgeIndex`, `Knowledge`, or `KnowledgeRanking`.
        recursive: If True, includes files from subdirectories in counting.

    Returns:
        Directory scores with file count per directory.
    """
    return directory_sum_scores(constant_scores(keys), recursive=recursive)

__all__ = [
    'directory_max_scores',
    'directory_sum_scores',
    'directory_count_scores',
]
