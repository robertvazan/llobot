"""
Knowledge management system for llobot.

This module provides the core Knowledge class and directory loading functionality.
Knowledge represents a collection of documents indexed by Path, supporting various
operations like filtering, transformation, and combination with other knowledge sets.

Submodules and Subpackages
---------------------------

indexes
    KnowledgeIndex for path-based indexing and set operations
rankings
    KnowledgeRanking for ordered sequences of knowledge paths
scores
    KnowledgeScores for scoring and weighting knowledge items
graphs
    KnowledgeGraph for relationship graphs between knowledge items
trees
    KnowledgeTree for hierarchical directory tree representations
subsets/
    Pattern-based filtering and selection with KnowledgeSubset
deltas/
    Change tracking with DocumentDelta and KnowledgeDelta
sources
    Knowledge sources
archives
    Historical knowledge storage
rankers
    Ranking algorithm implementations
scorers
    Knowledge scoring implementations
fs
    File system storage of knowledge
tgz
    Compressed knowledge archives

Functions
---------

load_directory_knowledge()
    Load knowledge from filesystem directory with filtering options
"""
from __future__ import annotations
from pathlib import Path
from llobot.chats.branches import ChatBranch
from llobot.fs import read_document

class Knowledge:
    _documents: dict[Path, str]
    _hash: int | None

    def __init__(self, documents: dict[Path, str] = {}):
        self._documents = dict(documents)
        self._hash = None

    def __str__(self) -> str:
        return str(self.keys())

    def keys(self) -> 'KnowledgeIndex':
        from llobot.knowledge.indexes import KnowledgeIndex
        return KnowledgeIndex(self._documents.keys())

    def __len__(self) -> int:
        return len(self._documents)

    @property
    def cost(self) -> int:
        return sum(len(content) for content in self._documents.values())

    def __bool__(self) -> bool:
        return bool(self._documents)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Knowledge):
            return NotImplemented
        return self._documents == other._documents

    def __hash__(self) -> int:
        if self._hash is None:
            self._hash = hash(frozenset(self._documents.items()))
        return self._hash

    def __contains__(self, path: Path | str) -> bool:
        return Path(path) in self._documents

    def __getitem__(self, path: Path) -> str:
        return self._documents.get(path, '')

    def __iter__(self) -> Iterator[(Path, str)]:
        return iter(self._documents.items())

    def transform(self, operation: Callable[[Path, str], str]) -> Knowledge:
        return Knowledge({path: operation(path, content) for path, content in self})

    def __and__(self, subset: 'KnowledgeSubset' | str | Path | 'KnowledgeIndex' | 'KnowledgeRanking' | 'KnowledgeScores') -> Knowledge:
        from llobot.knowledge.subsets import coerce_subset
        subset = coerce_subset(subset)
        return Knowledge({path: content for path, content in self if path in subset})

    def __or__(self, addition: Knowledge) -> Knowledge:
        return Knowledge(self._documents | addition._documents)

    def __sub__(self, subset: 'KnowledgeSubset' | str | Path | 'KnowledgeIndex' | Path | 'KnowledgeRanking' | 'KnowledgeScores') -> Knowledge:
        from llobot.knowledge.subsets import coerce_subset
        return self & ~coerce_subset(subset)

    def __rtruediv__(self, prefix: Path | str) -> Knowledge:
        prefix = Path(prefix)
        return Knowledge({prefix/path: content for path, content in self})

    def __truediv__(self, subtree: Path | str) -> Knowledge:
        subtree = Path(subtree)
        return Knowledge({path.relative_to(subtree): content for path, content in self if path.is_relative_to(subtree)})

_default_subset = object()

def load_directory_knowledge(
    directory: Path | str,
    whitelist: 'KnowledgeSubset' | str | Path | 'KnowledgeIndex' | 'KnowledgeRanking' | None | object = _default_subset,
    blacklist: 'KnowledgeSubset' | str | Path | 'KnowledgeIndex' | 'KnowledgeRanking' | None | object = _default_subset,
) -> Knowledge:
    from llobot.knowledge.indexes import KnowledgeIndex, directory_index, coerce_index
    from llobot.knowledge.rankings import KnowledgeRanking
    from llobot.knowledge.subsets import coerce_subset, whitelist_subset, blacklist_subset, match_nothing, match_everything
    directory = Path(directory)
    if whitelist is _default_subset:
        whitelist = whitelist_subset()
    if blacklist is _default_subset:
        blacklist = blacklist_subset()
    blacklist = coerce_subset(blacklist or match_nothing())
    # Special-case concrete whitelist, so that we don't recurse into potentially large directories unnecessarily.
    if isinstance(whitelist, (Path, KnowledgeIndex, KnowledgeRanking)):
        whitelist = coerce_index(whitelist)
        knowledge = Knowledge({path: read_document(directory/path) for path in whitelist if (directory/path).is_file() and path not in blacklist})
    else:
        whitelist = coerce_subset(whitelist or match_everything())
        index = directory_index(directory, whitelist, blacklist)
        knowledge = Knowledge({path: read_document(directory/path) for path in index})
    return knowledge

__all__ = [
    'Knowledge',
    'load_directory_knowledge',
]
