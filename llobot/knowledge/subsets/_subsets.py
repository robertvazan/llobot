from __future__ import annotations
import functools
from pathlib import Path

class KnowledgeSubset:
    @property
    def content_sensitive(self) -> bool:
        return True

    def accepts(self, path: Path, content: str = '') -> bool:
        raise NotImplementedError

    def __call__(self, path: Path, content: str = '') -> bool:
        return self.accepts(path, content)

    def __or__(self, other: KnowledgeSubset) -> KnowledgeSubset:
        from llobot.knowledge.subsets.unions import UnionKnowledgeSubset
        if isinstance(other, UnionKnowledgeSubset):
            return other | self
        return create(lambda path, content: self(path, content) or other(path, content), self.content_sensitive or other.content_sensitive)

    def __and__(self, other: KnowledgeSubset) -> KnowledgeSubset:
        return create(lambda path, content: self(path, content) and other(path, content), self.content_sensitive or other.content_sensitive)

    def __sub__(self, other: KnowledgeSubset) -> KnowledgeSubset:
        return create(lambda path, content: self(path, content) and not other(path, content), self.content_sensitive or other.content_sensitive)

    def __invert__(self) -> KnowledgeSubset:
        return create(lambda path, content: not self(path, content), self.content_sensitive)

def create(predicate: Callable[[Path, str], bool], content_sensitive: bool = True) -> KnowledgeSubset:
    class LambdaSubset(KnowledgeSubset):
        @property
        def content_sensitive(self) -> bool:
            return content_sensitive
        def accepts(self, path: Path, content: str = '') -> bool:
            return predicate(path, content)
    return LambdaSubset()

def path(predicate: Callable[[Path], bool]) -> KnowledgeSubset:
    return create(lambda path, content: predicate(path), False)

def solo(solo_path: Path) -> KnowledgeSubset:
    return path(lambda other_path: solo_path == other_path)

@functools.cache
def nothing() -> KnowledgeSubset:
    import llobot.knowledge.subsets.unions
    return llobot.knowledge.subsets.unions.union()

@functools.cache
def everything() -> KnowledgeSubset:
    return path(lambda path: True)

def suffix(*suffixes: str) -> KnowledgeSubset:
    import llobot.knowledge.subsets.unions
    return llobot.knowledge.subsets.unions.suffix(*suffixes)

def filename(*names: str) -> KnowledgeSubset:
    import llobot.knowledge.subsets.unions
    return llobot.knowledge.subsets.unions.filename(*names)

def directory(*directories: str) -> KnowledgeSubset:
    import llobot.knowledge.subsets.unions
    return llobot.knowledge.subsets.unions.directory(*directories)

def _ancestors(path: Path) -> list[Path]:
    while path != path.parent:
        yield path
        path = path.parent

def glob(*patterns: str) -> KnowledgeSubset:
    if not patterns:
        return nothing()
    if len(patterns) > 1:
        import llobot.knowledge.subsets.unions
        return llobot.knowledge.subsets.unions.union(*(glob(pattern) for pattern in patterns))
    pattern = patterns[0]
    if '/**/' in pattern:
        raise ValueError
    elif pattern.startswith('**/') and not pattern.endswith('/**'):
        pattern = pattern[3:]
        return path(lambda path: path.match(pattern))
    elif pattern.startswith('**/') and pattern.endswith('/**'):
        pattern = pattern[3:-3]
        return path(lambda path: any(ancestor.match(pattern) for ancestor in _ancestors(path)))
    elif not pattern.startswith('**/') and pattern.endswith('/**'):
        pattern = pattern[:-3]
        length = len(Path(pattern).parts)
        return path(lambda path: len(path.parts) >= length and Path(*path.parts[:length]).match(pattern))
    else:
        length = len(Path(pattern).parts)
        return path(lambda path: len(path.parts) == length and path.match(pattern))

def coerce(material: KnowledgeSubset | str | Path | 'KnowledgeIndex' | 'KnowledgeRanking' | 'KnowledgeScores' | 'Knowledge') -> KnowledgeSubset:
    if isinstance(material, KnowledgeSubset):
        return material
    if isinstance(material, str):
        return glob(material)
    if isinstance(material, Path):
        return solo(material)
    import llobot.knowledge.indexes
    index = llobot.knowledge.indexes.coerce(material)
    return path(lambda path: path in index)

# We will LRU-cache the cache() function itself, so that multiple requests to cache single subset do not create multiple memory-hungry caches.
@functools.lru_cache
def cache(uncached: KnowledgeSubset) -> KnowledgeSubset:
    if uncached.content_sensitive or uncached == everything() or uncached == nothing():
        return uncached
    memory = {}
    def accepts(path: Path) -> bool:
        accepted = memory.get(path, None)
        if accepted is None:
            # We will cache the result forever. There aren't going to be that many different paths.
            memory[path] = accepted = uncached(path)
        return accepted
    return path(accepts)

@functools.cache
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

@functools.cache
def blacklist() -> KnowledgeSubset:
    from llobot.knowledge.subsets import git, java, rust, vscode, eclipse
    return (git.blacklist()
        | java.blacklist()
        | rust.blacklist()
        | vscode.blacklist()
        | eclipse.blacklist())

@functools.cache
def boilerplate() -> KnowledgeSubset:
    from llobot.knowledge.subsets import git, repo, github, java
    return (git.boilerplate()
        | repo.boilerplate()
        | github.boilerplate()
        | java.boilerplate())

@functools.cache
def unimportant() -> KnowledgeSubset:
    from llobot.knowledge.subsets import java, rust, toml, xml
    return (boilerplate()
        | java.unimportant()
        | rust.unimportant()
        | toml.whitelist()
        | xml.whitelist())

__all__ = [
    'KnowledgeSubset',
    'create',
    'path',
    'solo',
    'nothing',
    'everything',
    'suffix',
    'filename',
    'directory',
    'glob',
    'coerce',
    'cache',
    'whitelist',
    'blacklist',
    'boilerplate',
    'unimportant',
]

