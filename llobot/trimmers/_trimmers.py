from __future__ import annotations
from functools import cache
import re as regexlib
from pathlib import Path
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.knowledge.indexes import KnowledgeIndex
import llobot.knowledge.subsets

class Trimmer:
    def trim(self, path: Path, content: str) -> str:
        raise NotImplementedError

    def __call__(self, path: Path, content: str) -> str:
        return self.trim(path, content)

    def trim_fully(self, path: Path, content: str) -> str:
        while True:
            trimmed = self.trim(path, content)
            if trimmed == content:
                return content
            content = trimmed

    def terminate(self) -> Trimmer:
        return first(self, terminal())

    def __and__(self, whitelist: KnowledgeSubset | str | KnowledgeIndex) -> Trimmer:
        whitelist = llobot.knowledge.subsets.coerce(whitelist)
        return create(lambda path, content: self(path, content) if whitelist(path, content) else content)

    def __add__(self, other: Trimmer) -> Trimmer:
        def trim(path: Path, content: str) -> str:
            trimmed = self(path, content)
            if trimmed == content:
                trimmed = other(path, content)
            return trimmed
        return create(trim)

    def __or__(self, other: Trimmer) -> Trimmer:
        def trim(path: Path, content: str) -> str:
            ours = self(path, content)
            theirs = other(path, content)
            return ours if len(ours) <= len(theirs) else theirs
        return create(trim)

def create(function: Callable[[Path, str], str]) -> Trimmer:
    class LambdaTrimmer(Trimmer):
        def trim(self, path: Path, content: str) -> str:
            return function(path, content)
    return LambdaTrimmer()

@cache
def none() -> Trimmer:
    return create(lambda path, content: content)

@cache
def terminal() -> Trimmer:
    return create(lambda path, content: '')

def first(*chain: Trimmer) -> Trimmer:
    def trim(path: Path, content: str) -> str:
        for trimmer in chain:
            trimmed = trimmer(path, content)
            if trimmed != content:
                return trimmed
        return content
    return create(trim)

def largest(*alternatives: Trimmer) -> Trimmer:
    def trim(path: Path, content: str) -> str:
        result = content
        for trimmer in alternatives:
            trimmed = trimmer(path, content)
            if len(trimmed) < len(result):
                result = trimmed
        return result
    return create(trim)

def re(pattern: str, flags=0, *, replacement: str = '', incremental=False) -> Trimmer:
    pattern = regexlib.compile(pattern, flags)
    if incremental:
        def trim(path: Path, content: str) -> str:
            # Make sure all lines are terminated with newline. It simplifies many regexes.
            content += '\n'
            matches = list(pattern.finditer(content))
            if not matches:
                return content.strip()
            largest = max(matches, key=lambda m: len(m.group(0)) - len(m.expand(replacement)))
            return (content[:largest.start()] + largest.expand(replacement) + content[largest.end():]).strip()
        return create(trim)
    else:
        return create(lambda path, content: pattern.sub(replacement, content+'\n').strip())

@cache
def tabs_to_spaces() -> Trimmer:
    return create(lambda path, content: content.replace('\t', '    '))

@cache
def blank_lines() -> Trimmer:
    return re(r'^ *$', regexlib.MULTILINE)

@cache
def normalize_whitespace() -> Trimmer:
    return tabs_to_spaces() + blank_lines()

@cache
def eager() -> Trimmer:
    from llobot.trimmers import markdown, python, java, rust, cpp, xml, toml
    return (markdown.eager()
        + python.eager()
        + java.eager()
        + rust.eager()
        + cpp.eager()
        + xml.eager()
        + toml.eager())

__all__ = [
    'Trimmer',
    'create',
    'none',
    'terminal',
    'first',
    'largest',
    're',
    'tabs_to_spaces',
    'blank_lines',
    'normalize_whitespace',
    'eager',
]

