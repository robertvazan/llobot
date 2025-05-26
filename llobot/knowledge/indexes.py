from __future__ import annotations
from pathlib import Path
from llobot.knowledge.subsets import KnowledgeSubset
import llobot.knowledge.subsets

class KnowledgeIndex:
    _paths: set[Path]

    def __init__(self, paths: Iterable[Path | str] = set()):
        self._paths = set(Path(path) for path in paths)

    def __str__(self) -> str:
        return str(self.sorted())

    def __len__(self) -> int:
        return len(self._paths)

    def __bool__(self) -> bool:
        return bool(self._paths)

    def __contains__(self, path: Path | str) -> bool:
        return Path(path) in self._paths

    def __iter__(self) -> Iterator[Path]:
        return iter(self._paths)

    def sorted(self) -> 'KnowledgeRanking':
        import llobot.knowledge.rankings
        return llobot.knowledge.rankings.lexicographical(self)

    def reversed(self) -> 'KnowledgeRanking':
        return self.sorted().reversed()

    def __and__(self, whitelist: KnowledgeSubset | str | KnowledgeIndex) -> KnowledgeIndex:
        return KnowledgeIndex(filter(llobot.knowledge.subsets.coerce(whitelist), self))

    def __or__(self, addition: Path | KnowledgeIndex) -> KnowledgeIndex:
        if isinstance(addition, Path):
            return self | KnowledgeIndex([addition])
        if isinstance(addition, KnowledgeIndex):
            return KnowledgeIndex(self._paths | addition._paths)
        raise TypeError

    def __sub__(self, blacklist: KnowledgeSubset | str | KnowledgeIndex | Path) -> KnowledgeIndex:
        return self & ~llobot.knowledge.subsets.coerce(blacklist)

    def __rtruediv__(self, prefix: Path | str) -> KnowledgeIndex:
        prefix = Path(prefix)
        return KnowledgeIndex(prefix/path for path in self)

    def __truediv__(self, subtree: Path | str) -> KnowledgeIndex:
        subtree = Path(subtree)
        return KnowledgeIndex(path.relative_to(subtree) for path in self if path.is_relative_to(subtree))

def coerce(what: KnowledgeIndex | 'Knowledge' | 'KnowledgeRanking' | 'KnowledgeScores') -> KnowledgeIndex:
    if isinstance(what, KnowledgeIndex):
        return what
    from llobot.knowledge import Knowledge
    if isinstance(what, Knowledge):
        return what.keys()
    from llobot.knowledge.rankings import KnowledgeRanking
    if isinstance(what, KnowledgeRanking):
        return KnowledgeIndex(what)
    from llobot.scores.knowledge import KnowledgeScores
    if isinstance(what, KnowledgeScores):
        return what.keys()
    raise TypeError

def _walk(root: Path, directory: Path, whitelist: KnowledgeSubset, blacklist: KnowledgeSubset) -> Iterable[Path]:
    for path in directory.iterdir():
        relative = path.relative_to(root)
        if blacklist(relative):
            continue
        if path.is_dir():
            yield from _walk(root, path, whitelist, blacklist)
        elif whitelist(relative):
            yield relative

# Blacklist is separate, because it is applied to whole directories in addition to files whereas whitelist is applied only to individual files.
def directory(
    root: Path | str,
    whitelist: KnowledgeSubset | str | Path | KnowledgeIndex | 'KnowledgeRanking' | None = llobot.knowledge.subsets.whitelist(),
    blacklist: KnowledgeSubset | str | Path | KnowledgeIndex | 'KnowledgeRanking' | None = llobot.knowledge.subsets.blacklist(),
) -> KnowledgeIndex:
    from llobot.knowledge.rankings import KnowledgeRanking
    root = Path(root)
    if not root.exists():
        return KnowledgeIndex()
    blacklist = llobot.knowledge.subsets.cache(llobot.knowledge.subsets.coerce(blacklist or llobot.knowledge.subsets.nothing()))
    # Special-case concrete whitelist, so that we don't recurse into potentially large directories unnecessarily.
    if isinstance(whitelist, (Path, KnowledgeIndex, KnowledgeRanking)):
        whitelist = coerce(whitelist)
        return KnowledgeIndex([path for path in whitelist if (root/path).is_file() and not blacklist(path)])
    whitelist = llobot.knowledge.subsets.cache(llobot.knowledge.subsets.coerce(whitelist or llobot.knowledge.subsets.everything()))
    # Carefully walk the tree recursively, so that we can blacklist entire directories.
    return KnowledgeIndex(_walk(root, root, whitelist, blacklist))

__all__ = [
    'KnowledgeIndex',
    'coerce',
    'directory',
]

