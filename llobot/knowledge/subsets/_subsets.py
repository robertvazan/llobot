from __future__ import annotations
from functools import cache
from pathlib import Path

class KnowledgeSubset:
    def contains(self, path: Path) -> bool:
        raise NotImplementedError

    def __contains__(self, path: Path) -> bool:
        try:
            memory = self._memory
        except AttributeError:
            memory = self._memory = {}
        accepted = memory.get(path, None)
        if accepted is None:
            # We will cache the result forever. There aren't going to be that many different paths.
            memory[path] = accepted = self.contains(path)
        return accepted

    def __or__(self, other: KnowledgeSubset) -> KnowledgeSubset:
        from llobot.knowledge.subsets.unions import UnionKnowledgeSubset
        if isinstance(other, UnionKnowledgeSubset):
            return other | self
        return create(lambda path: self.contains(path) or other.contains(path))

    def __and__(self, other: KnowledgeSubset) -> KnowledgeSubset:
        return create(lambda path: self.contains(path) and other.contains(path))

    def __sub__(self, other: KnowledgeSubset) -> KnowledgeSubset:
        return create(lambda path: self.contains(path) and not other.contains(path))

    def __invert__(self) -> KnowledgeSubset:
        return create(lambda path: not self.contains(path))

def create(predicate: Callable[[Path], bool]) -> KnowledgeSubset:
    class LambdaSubset(KnowledgeSubset):
        def contains(self, path: Path) -> bool:
            return predicate(path)
    return LambdaSubset()

def solo(solo_path: Path) -> KnowledgeSubset:
    return create(lambda other_path: solo_path == other_path)

@cache
def nothing() -> KnowledgeSubset:
    import llobot.knowledge.subsets.unions
    return llobot.knowledge.subsets.unions.union()

@cache
def everything() -> KnowledgeSubset:
    return create(lambda path: True)

def suffix(*suffixes: str) -> KnowledgeSubset:
    import llobot.knowledge.subsets.unions
    return llobot.knowledge.subsets.unions.suffix(*suffixes)

def filename(*names: str) -> KnowledgeSubset:
    import llobot.knowledge.subsets.unions
    return llobot.knowledge.subsets.unions.filename(*names)

def directory(*directories: str) -> KnowledgeSubset:
    import llobot.knowledge.subsets.unions
    return llobot.knowledge.subsets.unions.directory(*directories)

def glob(*patterns: str) -> KnowledgeSubset:
    if not patterns:
        return nothing()
    if len(patterns) > 1:
        import llobot.knowledge.subsets.unions
        return llobot.knowledge.subsets.unions.union(*(glob(pattern) for pattern in patterns))
    pattern = patterns[0]
    return create(lambda path: path.full_match(pattern))

def coerce(material: KnowledgeSubset | str | Path | 'KnowledgeIndex' | 'KnowledgeRanking' | 'KnowledgeScores' | 'Knowledge') -> KnowledgeSubset:
    if isinstance(material, KnowledgeSubset):
        return material
    if isinstance(material, str):
        return glob(material)
    if isinstance(material, Path):
        return solo(material)
    import llobot.knowledge.indexes
    index = llobot.knowledge.indexes.coerce(material)
    return create(lambda path: path in index)

@cache
def whitelist() -> KnowledgeSubset:
    from llobot.knowledge.subsets import git, repo, github, markdown, python, java, rust, shell, cpp, xml, toml, txt
    return (git.whitelist()
        | repo.whitelist()
        | github.whitelist()
        | markdown.whitelist()
        | python.whitelist()
        | java.whitelist()
        | rust.whitelist()
        | shell.whitelist()
        | cpp.whitelist()
        | xml.whitelist()
        | toml.whitelist()
        | txt.whitelist())

@cache
def blacklist() -> KnowledgeSubset:
    from llobot.knowledge.subsets import git, java, rust, vscode, eclipse
    return (git.blacklist()
        | java.blacklist()
        | rust.blacklist()
        | vscode.blacklist()
        | eclipse.blacklist())

# What we almost never want to put in the context.
# This mostly covers files that are predictable and rarely edited.
@cache
def boilerplate() -> KnowledgeSubset:
    from llobot.knowledge.subsets import git, repo, github, java
    return (git.boilerplate()
        | repo.boilerplate()
        | github.boilerplate())

# Ancillary files accompany core files. They are always secondary in some way.
# They are included in the context, but their default weight is much lower.
# This also matches boilerplate files, so that it's a superset of boilerplate.
@cache
def ancillary() -> KnowledgeSubset:
    from llobot.knowledge.subsets import java, python, rust, toml, xml
    return (boilerplate()
        | java.ancillary()
        | python.ancillary()
        | rust.ancillary()
        | toml.whitelist())

__all__ = [
    'KnowledgeSubset',
    'create',
    'solo',
    'nothing',
    'everything',
    'suffix',
    'filename',
    'directory',
    'glob',
    'coerce',
    'whitelist',
    'blacklist',
    'boilerplate',
    'ancillary',
]
