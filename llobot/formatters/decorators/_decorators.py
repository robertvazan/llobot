from __future__ import annotations
from functools import cache, lru_cache
from pathlib import Path
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.knowledge.indexes import KnowledgeIndex
import llobot.knowledge.subsets
from llobot.formatters.paths import PathFormatter
import llobot.formatters.paths

# May add a header that identifies the document if the document is not self-identifying like a Java source file.
# If path is used for decoration, it can be abbreviated if full path is not necessary for identification.
# Decorators must be applied after trimming, so that they don't interfere with the trimming process.
class Decorator:
    def decorate(self, path: Path, content: str, note: str = '') -> str:
        raise NotImplementedError

    def __call__(self, path: Path, content: str, note: str = '') -> str:
        return self.decorate(path, content, note)

    def __or__(self, other: Decorator) -> Decorator:
        def decorate(path: Path, content: str, note: str = '') -> str:
            decorated = self(path, content, note)
            if decorated == content:
                decorated = other(path, content, note)
            return decorated
        return create(decorate)

    def __and__(self, whitelist: KnowledgeSubset | str | KnowledgeIndex) -> Decorator:
        whitelist = llobot.knowledge.subsets.coerce(whitelist)
        return create(lambda path, content, note: self(path, content, note) if whitelist(path, content) else content)

def create(function: Callable[[Path, str, str], str]) -> Decorator:
    class LambdaDecorator(Decorator):
        def decorate(self, path: Path, content: str, note: str = '') -> str:
            return function(path, content, note)
    return LambdaDecorator()

@cache
def none() -> Decorator:
    return create(lambda path, content, note: content)

@lru_cache
def pattern(syntax: str = '{}\n', paths: PathFormatter = llobot.formatters.paths.comment()) -> Decorator:
    return create(lambda path, content, note: (syntax.format(paths(path, note)) + content).strip())

@cache
def path(syntax: str = '{}\n') -> Decorator:
    return pattern(syntax)

@cache
def filename(syntax: str = '{}\n') -> Decorator:
    return pattern(syntax, llobot.formatters.paths.filename() | llobot.formatters.paths.comment())

@cache
def abbreviated(syntax: str = '{}\n') -> Decorator:
    return pattern(syntax, llobot.formatters.paths.abbreviated() | llobot.formatters.paths.comment())

@lru_cache
def details(paths: PathFormatter = llobot.formatters.paths.comment()) -> Decorator:
    return create(lambda path, content, note: f'<details>\n<summary>{paths(path, note)}</summary>\n\n{content.strip()}\n\n</details>')

@cache
def minimal() -> Decorator:
    from llobot.formatters.decorators import markdown, python, java, rust, cpp, xml, toml, properties, txt
    return (markdown.details()
        | python.path()
        | java.minimal()
        | rust.path()
        | cpp.path()
        | xml.path()
        | toml.path()
        | properties.path()
        | txt.standard())

__all__ = [
    'Decorator',
    'create',
    'none',
    'pattern',
    'path',
    'filename',
    'abbreviated',
    'details',
    'minimal',
]

