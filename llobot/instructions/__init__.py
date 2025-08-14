from __future__ import annotations
from functools import cache
from importlib import resources
import inspect
import llobot.text

def read(filename: str, *, package: str | None = None) -> str:
    if package is None:
        frame = inspect.currentframe().f_back
        package = frame.f_globals['__name__']
    content = (resources.files(package) / filename).read_text()
    return llobot.text.normalize(content).strip()

def combine(*sections: str) -> list[str]:
    seen = set()
    result = []
    for section in sections:
        section = section.strip()
        if section and section not in seen:
            seen.add(section)
            result.append(section)
    return result

def compile(role: str, *sections: str, title: str = 'Instructions') -> str:
    parts = [f'# {title}', role]
    parts.extend(combine(*sections))
    return llobot.text.concat(*parts)

class SystemPrompt:
    title: str
    role: str
    sections: list[str]

    def __init__(self, role: str, *sections: str, title: str = 'Instructions'):
        self.title = title
        self.role = role
        self.sections = combine(*sections)

    def compile(self) -> str:
        return compile(self.role, *self.sections, title=self.title)

def prepare(role: str, *sections: str, title: str = 'Instructions') -> SystemPrompt:
    return SystemPrompt(role, *sections, title=title)

@cache
def blocks() -> list[str]:
    return combine(read('blocks.md'))

@cache
def listings() -> list[str]:
    return combine(*blocks(), read('listings.md'))

@cache
def flags() -> list[str]:
    return combine(*listings(), read('flags.md'))

@cache
def knowledge() -> list[str]:
    return combine(*listings(), read('knowledge.md'))

@cache
def edits() -> list[str]:
    return combine(*knowledge(), *flags(), read('edits.md'))

@cache
def diffs() -> list[str]:
    return combine(*edits(), read('diffs.md'))

@cache
def editing() -> list[str]:
    return combine(*diffs(), read('editing.md'))

@cache
def coding() -> list[str]:
    return combine(*editing(), read('coding.md'))

@cache
def documentation() -> list[str]:
    return combine(*coding(), read('documentation.md'))

@cache
def answering() -> list[str]:
    return combine(*knowledge(), *flags(), read('answering.md'))

@cache
def reviews() -> list[str]:
    return combine(*coding(), read('reviews.md'))

__all__ = [
    'read',
    'combine',
    'compile',
    'SystemPrompt',
    'prepare',
    'blocks',
    'listings',
    'flags',
    'knowledge',
    'edits',
    'diffs',
    'editing',
    'coding',
    'documentation',
    'answering',
    'reviews',
]
