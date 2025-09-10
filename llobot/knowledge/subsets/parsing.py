"""
Parsers for creating `KnowledgeSubset` instances from strings and files.
"""
from __future__ import annotations
from functools import cache
import inspect
from importlib import resources
import re
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.knowledge.subsets.directory import DirectorySubset
from llobot.knowledge.subsets.empty import EmptySubset
from llobot.knowledge.subsets.filename import FilenameSubset
from llobot.knowledge.subsets.pattern import PatternSubset, SimplePatternSubset
from llobot.knowledge.subsets.suffix import SuffixSubset
from llobot.knowledge.subsets.union import UnionSubset

# Compiled regexes for pattern detection
_SUFFIX_PATTERN = re.compile(r'^\*\.([^./]+)$')
_FILENAME_PATTERN = re.compile(r'^[^*?/]+$')
_DIRECTORY_PATTERN = re.compile(r'^([^*?/]+)/\*\*$')


def parse_pattern(*patterns: str) -> KnowledgeSubset:
    """
    Create a subset by parsing one or more glob-like patterns.

    This function performs several optimizations by classifying patterns:
    - `*.ext`: handled by `SuffixSubset`.
    - Plain filenames: handled by `FilenameSubset`.
    - `dir/**`: handled by `DirectorySubset`.
    - Patterns with `**` or starting with `/`: handled by `PatternSubset`.
    - Other simple patterns: handled by `SimplePatternSubset` (`path.match`).

    Args:
        *patterns: The glob patterns to parse.

    Returns:
        A `KnowledgeSubset` representing the union of all patterns.
    """
    if not patterns:
        return EmptySubset()

    suffixes = []
    filenames = []
    directories = []
    simple_patterns = []
    full_patterns = []

    for pattern in patterns:
        suffix_match = _SUFFIX_PATTERN.match(pattern)
        if suffix_match:
            suffixes.append('.' + suffix_match.group(1))
        elif _FILENAME_PATTERN.match(pattern):
            filenames.append(pattern)
        elif directory_match := _DIRECTORY_PATTERN.match(pattern):
            directories.append(directory_match.group(1))
        elif pattern.startswith('/') or '**' in pattern:
            full_patterns.append(pattern)
        else:
            simple_patterns.append(pattern)

    subsets = []
    if suffixes:
        subsets.append(SuffixSubset(*suffixes))
    if filenames:
        subsets.append(FilenameSubset(*filenames))
    if directories:
        subsets.append(DirectorySubset(*directories))
    for pattern in simple_patterns:
        subsets.append(SimplePatternSubset(pattern))
    for pattern in full_patterns:
        is_absolute = pattern.startswith('/')
        p = pattern[1:] if is_absolute else pattern
        if not is_absolute:
             p = '**/' + p
        subsets.append(PatternSubset(p))

    if not subsets:
        return EmptySubset()
    if len(subsets) == 1:
        return subsets[0]
    return UnionSubset(*subsets)


def parse_subset(text: str) -> KnowledgeSubset:
    """
    Parse patterns from a block of text.

    Each line is treated as a pattern. Blank lines and comments (starting
    with `#`) are ignored.

    Args:
        text: The text containing patterns.

    Returns:
        A `KnowledgeSubset` from the parsed patterns.
    """
    patterns = []
    for line in text.splitlines():
        # Remove comments (everything after #)
        comment_pos = line.find('#')
        if comment_pos >= 0:
            line = line[:comment_pos]
        line = line.strip()
        if line:
            patterns.append(line)
    return parse_pattern(*patterns)


def load_subset(filename: str, *, package: str | None = None) -> KnowledgeSubset:
    """
    Load patterns from a resource file and parse them into a subset.

    Args:
        filename: The name of the resource file.
        package: The package where the resource file is located. If `None`,
                 it's inferred from the caller's context.

    Returns:
        A `KnowledgeSubset` from the patterns in the file.
    """
    if package is None:
        frame = inspect.currentframe().f_back
        package = frame.f_globals['__name__']
    content = (resources.files(package) / filename).read_text()
    return parse_subset(content)


__all__ = [
    'parse_pattern',
    'parse_subset',
    'load_subset',
]
