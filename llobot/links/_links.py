from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex

# Implementations must be usable as dict keys.
class Link:
    # All links currently work on paths, but the content parameter could be useful in the future.
    def matches(self, path: Path, content: str = '') -> bool:
        raise NotImplementedError

    # Iterating over the whole knowledge is somewhat inefficient, but we can optimize later by introducing some kind of prebuilt knowledge graph.
    # This method could also accept KnowledgeIndex for quick matching without content, but we don't need that now.
    def resolve(self, knowledge: Knowledge) -> set[Path]:
        return {path for path, content in knowledge if self.matches(path, content)}

    def resolve_indexed(self, knowledge: Knowledge, indexes: dict[type, object]) -> set[Path]:
        return self.resolve(knowledge)

@dataclass(frozen=True)
class _AbsolutePathLink(Link):
    path: Path

    def matches(self, path: Path, content: str = '') -> bool:
        return path == self.path

    def resolve(self, knowledge: Knowledge) -> set[Path]:
        return {self.path} if self.path in knowledge else set()

def absolute(path: Path | str) -> Link:
    return _AbsolutePathLink(Path(path))

class _AbbreviatedPathIndex:
    matches: dict[Path, set[Path]]

    def __init__(self, knowledge: Knowledge):
        matches = {}
        for path in knowledge.keys():
            segments = path.parts
            for length in range(1, len(segments) + 1):
                abbreviated = Path(*segments[-length:])
                if not abbreviated in matches:
                    matches[abbreviated] = set()
                matches[abbreviated].add(path)
        self.matches = matches

@dataclass(frozen=True)
class _AbbreviatedPathLink(Link):
    name: str
    path: Path

    def matches(self, path: Path, content: str = '') -> bool:
        return path.name == self.name and path.match(self.path)

    def resolve_indexed(self, knowledge: Knowledge, indexes: dict[type, object]) -> set[Path]:
        if _AbbreviatedPathIndex not in indexes:
            indexes[_AbbreviatedPathIndex] = _AbbreviatedPathIndex(knowledge)
        index = indexes[_AbbreviatedPathIndex]
        return index.matches.get(self.path, set())

def abbreviated(path: Path | str) -> Link:
    path = Path(path)
    return _AbbreviatedPathLink(path.name, path)

class _FilenameIndex:
    matches: dict[str, set[Path]]

    def __init__(self, knowledge: Knowledge):
        matches = {}
        for path in knowledge.keys():
            if not path.name in matches:
                matches[path.name] = set()
            matches[path.name].add(path)
        self.matches = matches

@dataclass(frozen=True)
class _FilenameLink(Link):
    name: str

    def matches(self, path: Path, content: str = '') -> bool:
        return path.name == self.name

    def resolve_indexed(self, knowledge: Knowledge, indexes: dict[type, object]) -> set[Path]:
        if _FilenameIndex not in indexes:
            indexes[_FilenameIndex] = _FilenameIndex(knowledge)
        index = indexes[_FilenameIndex]
        return index.matches.get(self.name, set())

def filename(name: str) -> Link:
    return _FilenameLink(name)

__all__ = [
    'Link',
    'absolute',
    'abbreviated',
    'filename',
]
