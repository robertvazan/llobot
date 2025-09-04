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
        return create_subset(lambda path: self.contains(path) or other.contains(path))

    def __and__(self, other: KnowledgeSubset) -> KnowledgeSubset:
        return create_subset(lambda path: self.contains(path) and other.contains(path))

    def __sub__(self, other: KnowledgeSubset) -> KnowledgeSubset:
        return create_subset(lambda path: self.contains(path) and not other.contains(path))

    def __invert__(self) -> KnowledgeSubset:
        return create_subset(lambda path: not self.contains(path))

def create_subset(predicate: Callable[[Path], bool]) -> KnowledgeSubset:
    class LambdaSubset(KnowledgeSubset):
        def contains(self, path: Path) -> bool:
            return predicate(path)
    return LambdaSubset()

def match_solo(solo_path: Path) -> KnowledgeSubset:
    return create_subset(lambda other_path: solo_path == other_path)

@cache
def match_nothing() -> KnowledgeSubset:
    return create_subset(lambda path: False)

@cache
def match_everything() -> KnowledgeSubset:
    return create_subset(lambda path: True)

def match_suffix(*suffixes: str) -> KnowledgeSubset:
    if not suffixes:
        return match_nothing()
    suffix_set = set(suffixes)
    return create_subset(lambda path: path.suffix in suffix_set)

def match_filename(*names: str) -> KnowledgeSubset:
    if not names:
        return match_nothing()
    name_set = set(names)
    return create_subset(lambda path: path.name in name_set)

def match_directory(*directories: str) -> KnowledgeSubset:
    if not directories:
        return match_nothing()
    directory_set = set(directories)
    return create_subset(lambda path: any(part in directory_set for part in path.parts))

def match_relative(pattern: str) -> KnowledgeSubset:
    """Create subset matching simple relative pattern using Path.match()."""
    return create_subset(lambda path: path.match(pattern))

def match_absolute(pattern: str) -> KnowledgeSubset:
    """Create subset matching absolute pattern using Path.full_match()."""
    return create_subset(lambda path: path.full_match(pattern))

def match_glob(*patterns: str) -> KnowledgeSubset:
    """Create subset matching glob patterns with optimized handling."""
    if not patterns:
        return match_nothing()

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
        subsets.append(match_suffix(*suffixes))
    if filenames:
        subsets.append(match_filename(*filenames))
    if directories:
        subsets.append(match_directory(*directories))
    for pattern in relatives:
        subsets.append(match_relative(pattern))
    for pattern in absolutes:
        subsets.append(match_absolute(pattern))

    # Chain unions
    if not subsets:
        return match_nothing()
    result = subsets[0]
    for subset in subsets[1:]:
        result = result | subset
    return result

def parse_subset(text: str) -> KnowledgeSubset:
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
    return match_glob(*patterns)

def load_subset(filename: str, *, package: str | None = None) -> KnowledgeSubset:
    """Load patterns from resource file."""
    if package is None:
        frame = inspect.currentframe().f_back
        package = frame.f_globals['__name__']
    content = (resources.files(package) / filename).read_text()
    return parse_subset(content)

def coerce_subset(material: KnowledgeSubset | str | Path | 'KnowledgeIndex' | 'KnowledgeRanking' | 'KnowledgeScores' | 'Knowledge') -> KnowledgeSubset:
    if isinstance(material, KnowledgeSubset):
        return material
    if isinstance(material, str):
        return match_glob(material)
    if isinstance(material, Path):
        return match_solo(material)
    import llobot.knowledge.indexes
    index = llobot.knowledge.indexes.coerce_index(material)
    return create_subset(lambda path: path in index)

@cache
def whitelist_subset() -> KnowledgeSubset:
    return load_subset('whitelist.txt')

@cache
def blacklist_subset() -> KnowledgeSubset:
    return load_subset('blacklist.txt')

# What we almost never want to put in the context.
# This mostly covers files that are predictable and rarely edited.
@cache
def boilerplate_subset() -> KnowledgeSubset:
    return load_subset('boilerplate.txt')

@cache
def overviews_subset() -> KnowledgeSubset:
    return load_subset('overviews.txt')

# Ancillary files accompany core files. They are always secondary in some way.
# They are included in the context, but their default weight is much lower.
# This also matches boilerplate files, so that it's a superset of boilerplate.
@cache
def ancillary_subset() -> KnowledgeSubset:
    return (boilerplate_subset() | load_subset('ancillary.txt')) - overviews_subset()

__all__ = [
    'KnowledgeSubset',
    'create_subset',
    'match_solo',
    'match_nothing',
    'match_everything',
    'match_suffix',
    'match_filename',
    'match_directory',
    'match_relative',
    'match_absolute',
    'match_glob',
    'parse_subset',
    'load_subset',
    'coerce_subset',
    'whitelist_subset',
    'blacklist_subset',
    'boilerplate_subset',
    'overviews_subset',
    'ancillary_subset',
]
