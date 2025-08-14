from __future__ import annotations
from functools import cache
from pathlib import Path
from importlib import resources
import inspect
import re

# Compiled regexes for pattern detection
_SUFFIX_PATTERN = re.compile(r'^\*\.([^./]+)$')
_FILENAME_PATTERN = re.compile(r'^[^*?/]+$')
_DIRECTORY_PATTERN = re.compile(r'^([^*?/]+)/\*\*$')

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
    return create(lambda path: False)

@cache
def everything() -> KnowledgeSubset:
    return create(lambda path: True)

def suffix(*suffixes: str) -> KnowledgeSubset:
    if not suffixes:
        return nothing()
    suffix_set = set(suffixes)
    return create(lambda path: path.suffix in suffix_set)

def filename(*names: str) -> KnowledgeSubset:
    if not names:
        return nothing()
    name_set = set(names)
    return create(lambda path: path.name in name_set)

def directory(*directories: str) -> KnowledgeSubset:
    if not directories:
        return nothing()
    directory_set = set(directories)
    return create(lambda path: any(part in directory_set for part in path.parts))

def relative(pattern: str) -> KnowledgeSubset:
    """Create subset matching simple relative pattern using Path.match()."""
    return create(lambda path: path.match(pattern))

def absolute(pattern: str) -> KnowledgeSubset:
    """Create subset matching absolute pattern using Path.full_match()."""
    return create(lambda path: path.full_match(pattern))

def glob(*patterns: str) -> KnowledgeSubset:
    """Create subset matching glob patterns with optimized handling."""
    if not patterns:
        return nothing()

    suffixes = []
    filenames = []
    directories = []
    relatives = []
    absolutes = []

    for pattern in patterns:
        is_absolute = pattern.startswith('/')

        if is_absolute:
            pattern = pattern[1:]  # Strip leading /

        # Check for suffix pattern (*.ext where ext has no dots)
        suffix_match = _SUFFIX_PATTERN.match(pattern)
        if suffix_match:
            suffixes.append('.' + suffix_match.group(1))
        # Check for filename pattern (no wildcards or slashes)
        elif _FILENAME_PATTERN.match(pattern):
            filenames.append(pattern)
        # Check for directory pattern (dirname/**)
        elif directory_match := _DIRECTORY_PATTERN.match(pattern):
            directories.append(directory_match.group(1))
        # Simple relative pattern (no ** or initial /)
        elif not is_absolute and '**' not in pattern:
            relatives.append(pattern)
        # Everything else goes to absolute patterns
        else:
            if not is_absolute:
                pattern = '**/' + pattern
            absolutes.append(pattern)

    subsets = []

    if suffixes:
        subsets.append(suffix(*suffixes))
    if filenames:
        subsets.append(filename(*filenames))
    if directories:
        subsets.append(directory(*directories))
    for pattern in relatives:
        subsets.append(relative(pattern))
    for pattern in absolutes:
        subsets.append(absolute(pattern))

    # Chain unions
    if not subsets:
        return nothing()
    result = subsets[0]
    for subset in subsets[1:]:
        result = result | subset
    return result

def parse(text: str) -> KnowledgeSubset:
    """Parse patterns from text, ignoring comments and blank lines."""
    patterns = []
    for line in text.splitlines():
        # Remove comments (everything after #)
        comment_pos = line.find('#')
        if comment_pos >= 0:
            line = line[:comment_pos]
        line = line.strip()
        if line:
            patterns.append(line)
    return glob(*patterns)

def load(filename: str, *, package: str | None = None) -> KnowledgeSubset:
    """Load patterns from resource file."""
    if package is None:
        frame = inspect.currentframe().f_back
        package = frame.f_globals['__name__']
    content = (resources.files(package) / filename).read_text()
    return parse(content)

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
    return load('whitelist.txt')

@cache
def blacklist() -> KnowledgeSubset:
    return load('blacklist.txt')

# What we almost never want to put in the context.
# This mostly covers files that are predictable and rarely edited.
@cache
def boilerplate() -> KnowledgeSubset:
    return load('boilerplate.txt')

@cache
def overviews() -> KnowledgeSubset:
    return load('overviews.txt')

# Ancillary files accompany core files. They are always secondary in some way.
# They are included in the context, but their default weight is much lower.
# This also matches boilerplate files, so that it's a superset of boilerplate.
@cache
def ancillary() -> KnowledgeSubset:
    return (boilerplate() | load('ancillary.txt')) - overviews()

__all__ = [
    'KnowledgeSubset',
    'create',
    'solo',
    'nothing',
    'everything',
    'suffix',
    'filename',
    'directory',
    'relative',
    'absolute',
    'glob',
    'parse',
    'load',
    'coerce',
    'whitelist',
    'blacklist',
    'boilerplate',
    'overviews',
    'ancillary',
]
