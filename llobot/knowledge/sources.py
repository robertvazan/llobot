from __future__ import annotations
from pathlib import Path
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.rankings import KnowledgeRanking
from llobot.knowledge import Knowledge
import llobot.knowledge.subsets
import llobot.knowledge.indexes
import llobot.knowledge

class KnowledgeSource:
    def enumerate(self) -> KnowledgeIndex:
        raise NotImplementedError

    def load(self, filelist: KnowledgeIndex) -> Knowledge:
        raise NotImplementedError

    def load_all(self) -> Knowledge:
        return self.load(self.enumerate())

    def __or__(self, other: KnowledgeSource) -> KnowledgeSource:
        return create(
            enumerator=lambda: self.enumerate() | other.enumerate(),
            loader=lambda filelist: self.load(filelist) | other.load(filelist)
        )

    def __and__(self, subset: str | KnowledgeSubset) -> KnowledgeSource:
        subset = llobot.knowledge.subsets.coerce(subset)
        return create(
            enumerator=lambda: self.enumerate() & subset,
            loader=lambda filelist: self.load(filelist)
        )

    def __sub__(self, blacklist: str | KnowledgeSubset) -> KnowledgeSource:
        return self & ~llobot.knowledge.subsets.coerce(blacklist)

    def __truediv__(self, subtree: Path | str) -> KnowledgeSource:
        subtree = Path(subtree)
        return create(
            enumerator=lambda: self.enumerate()/subtree,
            loader=lambda filelist: self.load(subtree/filelist)/subtree
        )

    def __rtruediv__(self, prefix: Path | str) -> KnowledgeSource:
        prefix = Path(prefix)
        return create(
            enumerator=lambda: prefix/self.enumerate(),
            loader=lambda filelist: prefix/self.load(filelist/prefix)
        )

def create(enumerator: Callable[[], KnowledgeIndex], loader: Callable[[KnowledgeIndex], Knowledge]) -> KnowledgeSource:
    class LambdaSource(KnowledgeSource):
        def enumerate(self) -> KnowledgeIndex:
            return enumerator()
        def load(self, filelist: KnowledgeIndex) -> Knowledge:
            return loader(filelist)
    return LambdaSource()

def empty() -> KnowledgeSource:
    return create(
        enumerator=lambda: KnowledgeIndex(),
        loader=lambda _: Knowledge()
    )

def directory(
    directory: Path | str,
    whitelist: KnowledgeSubset | str | Path | KnowledgeIndex | KnowledgeRanking | None = llobot.knowledge.subsets.whitelist(),
    blacklist: KnowledgeSubset | str | Path | KnowledgeIndex | KnowledgeRanking | None = llobot.knowledge.subsets.blacklist(),
) -> KnowledgeSource:
    directory = Path(directory)
    return create(
        enumerator=lambda: llobot.knowledge.indexes.directory(directory, whitelist, blacklist),
        loader=lambda filelist: llobot.knowledge.directory(directory, filelist, None)
    )

__all__ = [
    'KnowledgeSource',
    'create',
    'empty',
    'directory',
]

