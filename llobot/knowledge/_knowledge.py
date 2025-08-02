from __future__ import annotations
from pathlib import Path
from llobot.chats import ChatBranch
import llobot.fs
import llobot.chats.markdown

class Knowledge:
    documents: dict[Path, str]
    _hash: int | None

    def __init__(self, documents: dict[Path, str] = {}):
        self.documents = {path: content for path, content in documents.items() if len(content) > 0}
        self._hash = None

    def __str__(self) -> str:
        return str(self.keys())

    def keys(self) -> 'KnowledgeIndex':
        from llobot.knowledge.indexes import KnowledgeIndex
        return KnowledgeIndex(self.documents.keys())

    def __len__(self) -> int:
        return len(self.documents)

    @property
    def cost(self) -> int:
        return sum(len(content) for content in self.documents.values())

    def __bool__(self) -> bool:
        return bool(self.documents)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Knowledge):
            return NotImplemented
        return self.documents == other.documents

    def __hash__(self) -> int:
        if self._hash is None:
            self._hash = hash(frozenset(self.documents.items()))
        return self._hash

    def __contains__(self, path: Path | str) -> bool:
        return Path(path) in self.documents

    def __getitem__(self, path: Path) -> str:
        return self.documents.get(path, '')

    def __iter__(self) -> Iterator[(Path, str)]:
        return iter(self.documents.items())

    def transform(self, operation: Callable[[Path, str], str]) -> Knowledge:
        return Knowledge({path: operation(path, content) for path, content in self})

    def __and__(self, subset: 'KnowledgeSubset' | str | Path | 'KnowledgeIndex' | 'KnowledgeRanking' | 'KnowledgeScores') -> Knowledge:
        import llobot.knowledge.subsets
        subset = llobot.knowledge.subsets.coerce(subset)
        return Knowledge({path: content for path, content in self if subset(path, content)})

    def __or__(self, addition: Knowledge) -> Knowledge:
        return Knowledge(self.documents | addition.documents)

    def __sub__(self, subset: 'KnowledgeSubset' | str | Path | 'KnowledgeIndex' | Path | 'KnowledgeRanking' | 'KnowledgeScores') -> Knowledge:
        import llobot.knowledge.subsets
        return self & ~llobot.knowledge.subsets.coerce(subset)

    def __rtruediv__(self, prefix: Path | str) -> Knowledge:
        prefix = Path(prefix)
        return Knowledge({prefix/path: content for path, content in self})

    def __truediv__(self, subtree: Path | str) -> Knowledge:
        subtree = Path(subtree)
        return Knowledge({path.relative_to(subtree): content for path, content in self if path.is_relative_to(subtree)})

_default_subset = object()

def directory(
    directory: Path | str,
    whitelist: 'KnowledgeSubset' | str | Path | 'KnowledgeIndex' | 'KnowledgeRanking' | None | object = _default_subset,
    blacklist: 'KnowledgeSubset' | str | Path | 'KnowledgeIndex' | 'KnowledgeRanking' | None | object = _default_subset,
) -> Knowledge:
    from llobot.knowledge.indexes import KnowledgeIndex
    from llobot.knowledge.rankings import KnowledgeRanking
    import llobot.knowledge.subsets
    import llobot.knowledge.indexes
    directory = Path(directory)
    if whitelist is _default_subset:
        whitelist = llobot.knowledge.subsets.whitelist()
    if blacklist is _default_subset:
        blacklist = llobot.knowledge.subsets.blacklist()
    blacklist = llobot.knowledge.subsets.coerce(blacklist or llobot.knowledge.subsets.nothing())
    # Special-case concrete whitelist, so that we don't recurse into potentially large directories unnecessarily.
    if isinstance(whitelist, (Path, KnowledgeIndex, KnowledgeRanking)):
        whitelist = llobot.knowledge.indexes.coerce(whitelist)
        knowledge = Knowledge({path: llobot.fs.read_document(directory/path) for path in whitelist if (directory/path).is_file() and not blacklist(path)})
    else:
        whitelist = llobot.knowledge.subsets.coerce(whitelist or llobot.knowledge.subsets.everything())
        index = llobot.knowledge.indexes.directory(directory, whitelist, blacklist)
        knowledge = Knowledge({path: llobot.fs.read_document(directory/path) for path in index})
        if whitelist.content_sensitive:
            knowledge &= whitelist
    if blacklist.content_sensitive:
        knowledge -= blacklist
    return knowledge

__all__ = [
    'Knowledge',
    'directory',
]
