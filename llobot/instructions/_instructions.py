from __future__ import annotations
from functools import cache
from importlib import resources
import inspect
import llobot.text

def read(filename: str, *, package: str | None = None) -> str:
    if package is None:
        frame = inspect.currentframe().f_back
        package = frame.f_globals['__name__']
    return (resources.files(package) / filename).read_text().strip()

def combine(*sections: str) -> list[str]:
    seen = set()
    result = []
    for section in sections:
        section = section.strip()
        if section and section not in seen:
            seen.add(section)
            result.append(section)
    return result

def compile(role: str, *sections: str) -> str:
    parts = ['# Instructions', role.strip()]
    parts.extend(combine(*sections))
    return llobot.text.concat(*parts)

@cache
def blocks() -> list[str]:
    return combine(read('blocks.md'))

@cache
def listings() -> list[str]:
    return combine(*blocks(), read('listings.md'))

@cache
def notes() -> list[str]:
    return combine(*listings(), read('notes.md'))

@cache
def deltas() -> list[str]:
    return combine(*listings(), *notes(), read('deltas.md'))

@cache
def knowledge() -> list[str]:
    return combine(*listings(), read('knowledge.md'))

@cache
def trimming() -> list[str]:
    return combine(*knowledge(), read('trimming.md'))

@cache
def edits() -> list[str]:
    return combine(*knowledge(), *trimming(), *deltas(), read('edits.md'))

@cache
def editing() -> list[str]:
    return combine(*edits(), read('editing.md'))

@cache
def coding() -> list[str]:
    return combine(*editing(), read('coding.md'))

@cache
def questions() -> list[str]:
    return combine(*coding(), read('questions.md'))

__all__ = [
    'read',
    'combine',
    'compile',
    'blocks',
    'listings',
    'notes',
    'deltas',
    'knowledge',
    'trimming',
    'edits',
    'editing',
    'coding',
    'questions',
]

