from __future__ import annotations
from pathlib import Path
from llobot.knowledge.subsets import KnowledgeSubset, coerce_subset, whitelist_subset, blacklist_subset
from llobot.knowledge.indexes import KnowledgeIndex, directory_index
from llobot.knowledge.rankings import KnowledgeRanking
from llobot.knowledge import Knowledge, load_directory_knowledge

class KnowledgeSource:
    def enumerate(self) -> KnowledgeIndex:
        raise NotImplementedError

    def load(self, filelist: KnowledgeIndex) -> Knowledge:
        raise NotImplementedError

    def load_all(self) -> Knowledge:
        return self.load(self.enumerate())

    def __or__(self, other: KnowledgeSource) -> KnowledgeSource:
        return create_knowledge_source(
            enumerator=lambda: self.enumerate() | other.enumerate(),
            loader=lambda filelist: self.load(filelist) | other.load(filelist)
        )

    def __and__(self, subset: str | KnowledgeSubset) -> KnowledgeSource:
        subset = coerce_subset(subset)
        return create_knowledge_source(
            enumerator=lambda: self.enumerate() & subset,
            loader=lambda filelist: self.load(filelist)
        )

    def __sub__(self, blacklist: str | KnowledgeSubset) -> KnowledgeSource:
        return self & ~coerce_subset(blacklist)

    def __truediv__(self, subtree: Path | str) -> KnowledgeSource:
        subtree = Path(subtree)
        return create_knowledge_source(
            enumerator=lambda: self.enumerate()/subtree,
            loader=lambda filelist: self.load(subtree/filelist)/subtree
        )

    def __rtruediv__(self, prefix: Path | str) -> KnowledgeSource:
        prefix = Path(prefix)
        return create_knowledge_source(
            enumerator=lambda: prefix/self.enumerate(),
            loader=lambda filelist: prefix/self.load(filelist/prefix)
        )

def create_knowledge_source(enumerator: Callable[[], KnowledgeIndex], loader: Callable[[KnowledgeIndex], Knowledge]) -> KnowledgeSource:
    class LambdaSource(KnowledgeSource):
        def enumerate(self) -> KnowledgeIndex:
            return enumerator()
        def load(self, filelist: KnowledgeIndex) -> Knowledge:
            return loader(filelist)
    return LambdaSource()

def empty_knowledge_source() -> KnowledgeSource:
    return create_knowledge_source(
        enumerator=lambda: KnowledgeIndex(),
        loader=lambda _: Knowledge()
    )

def directory_knowledge_source(
    directory: Path | str,
    whitelist: KnowledgeSubset | str | Path | KnowledgeIndex | KnowledgeRanking | None = whitelist_subset(),
    blacklist: KnowledgeSubset | str | Path | KnowledgeIndex | KnowledgeRanking | None = blacklist_subset(),
) -> KnowledgeSource:
    directory = Path(directory)
    return create_knowledge_source(
        enumerator=lambda: directory_index(directory, whitelist, blacklist),
        loader=lambda filelist: load_directory_knowledge(directory, filelist, None)
    )

__all__ = [
    'KnowledgeSource',
    'create_knowledge_source',
    'empty_knowledge_source',
    'directory_knowledge_source',
]
