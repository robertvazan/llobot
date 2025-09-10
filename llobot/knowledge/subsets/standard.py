"""
Pre-defined `KnowledgeSubset` instances for common use cases.
"""
from __future__ import annotations
from functools import cache
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.knowledge.subsets.parsing import load_subset
from llobot.knowledge.subsets.union import UnionSubset
from llobot.knowledge.subsets.difference import DifferenceSubset

@cache
def whitelist_subset() -> KnowledgeSubset:
    """
    A default whitelist, loaded from `whitelist.txt`.
    """
    return load_subset('whitelist.txt')

@cache
def blacklist_subset() -> KnowledgeSubset:
    """
    A default blacklist, loaded from `blacklist.txt`.
    """
    return load_subset('blacklist.txt')

@cache
def boilerplate_subset() -> KnowledgeSubset:
    """
    A subset for boilerplate files that are predictable and rarely edited.

    Loaded from `boilerplate.txt`.
    """
    return load_subset('boilerplate.txt')

@cache
def overviews_subset() -> KnowledgeSubset:
    """
    A subset for overview files (e.g., README.md, __init__.py).

    Loaded from `overviews.txt`.
    """
    return load_subset('overviews.txt')

@cache
def ancillary_subset() -> KnowledgeSubset:
    """
    A subset for ancillary files that accompany core files.

    These files are secondary and have lower weight in the context. This is
    a superset of boilerplate files but excludes overview files.
    """
    return (boilerplate_subset() | load_subset('ancillary.txt')) - overviews_subset()

__all__ = [
    'whitelist_subset',
    'blacklist_subset',
    'boilerplate_subset',
    'overviews_subset',
    'ancillary_subset',
]
