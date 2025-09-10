from __future__ import annotations
from functools import cache
from importlib import resources
import inspect
from llobot.utils.text import normalize_document, concat_documents

def read_prompt(filename: str, *, package: str | None = None) -> str:
    if package is None:
        frame = inspect.currentframe().f_back
        package = frame.f_globals['__name__']
    content = (resources.files(package) / filename).read_text()
    return normalize_document(content).strip()

class Prompt:
    """Base class for all prompt types."""

    def flatten(self) -> PromptFragment:
        """Converts the prompt to a flat list of sections."""
        return PromptFragment()

    def __str__(self) -> str:
        """Converts the prompt to a string."""
        return str(self.flatten())

class PromptFragment(Prompt):
    """Represents a flat list of prompt sections."""

    _sections: tuple[str, ...]

    def __init__(self, *sections: str | Prompt):
        # Flatten and deduplicate sections
        seen = set()
        result = []
        for section in sections:
            if isinstance(section, Prompt):
                fragment = section.flatten()
                for s in fragment._sections:
                    s = s.strip()
                    if s and s not in seen:
                        seen.add(s)
                        result.append(s)
            else:
                section = section.strip()
                if section and section not in seen:
                    seen.add(section)
                    result.append(section)
        self._sections = tuple(result)

    @property
    def sections(self) -> tuple[str, ...]:
        """Returns the sections tuple."""
        return self._sections

    def flatten(self) -> PromptFragment:
        """Returns self since this is already flattened."""
        return self

    def __str__(self) -> str:
        """Converts sections to a single string."""
        return concat_documents(*self._sections)

class PromptSection(Prompt):
    """Represents a prompt section with its prerequisite sections."""

    _section: str
    _prerequisites: tuple[str, ...]

    def __init__(self, section: str, *prerequisites: str | Prompt):
        self._section = section.strip()
        fragment = PromptFragment(*prerequisites)
        self._prerequisites = fragment._sections

    @property
    def section(self) -> str:
        """Returns the main section content."""
        return self._section

    @property
    def prerequisites(self) -> tuple[str, ...]:
        """Returns the prerequisite sections."""
        return self._prerequisites

    def flatten(self) -> PromptFragment:
        """Returns prerequisites followed by the main section."""
        return PromptFragment(*self._prerequisites, self._section)

class SystemPrompt(Prompt):
    """Represents a complete system prompt with role definition and sections."""

    _role: str
    _sections: tuple[str, ...]

    def __init__(self, role: str | SystemPrompt, *sections: str | Prompt):
        if isinstance(role, SystemPrompt):
            # Base prompt: adopt its role and prepend its sections
            self._role = role._role
            fragment = PromptFragment(*role._sections, *sections)
            self._sections = fragment._sections
        else:
            self._role = role.strip()
            fragment = PromptFragment(*sections)
            self._sections = fragment._sections

    @property
    def role(self) -> str:
        """Returns the role definition."""
        return self._role

    @property
    def sections(self) -> tuple[str, ...]:
        """Returns the sections."""
        return self._sections

    def flatten(self) -> PromptFragment:
        """Returns role followed by sections."""
        return PromptFragment(self._role, *self._sections)

@cache
def blocks_prompt_section() -> PromptSection:
    return PromptSection(read_prompt('blocks.md'))

@cache
def listings_prompt_section() -> PromptSection:
    return PromptSection(read_prompt('listings.md'), blocks_prompt_section())

@cache
def knowledge_prompt_section() -> PromptSection:
    return PromptSection(read_prompt('knowledge.md'), listings_prompt_section())

@cache
def deltas_prompt_section() -> PromptSection:
    return PromptSection(read_prompt('deltas.md'), knowledge_prompt_section())

@cache
def editing_prompt_section() -> PromptSection:
    return PromptSection(read_prompt('editing.md'), deltas_prompt_section())

@cache
def coding_prompt_section() -> PromptSection:
    return PromptSection(read_prompt('coding.md'), editing_prompt_section())

@cache
def documentation_prompt_section() -> PromptSection:
    return PromptSection(read_prompt('documentation.md'), coding_prompt_section())

@cache
def answering_prompt_section() -> PromptSection:
    return PromptSection(read_prompt('answering.md'), knowledge_prompt_section())

__all__ = [
    'read_prompt',
    'Prompt',
    'PromptFragment',
    'PromptSection',
    'SystemPrompt',
    'blocks_prompt_section',
    'listings_prompt_section',
    'knowledge_prompt_section',
    'deltas_prompt_section',
    'editing_prompt_section',
    'coding_prompt_section',
    'documentation_prompt_section',
    'answering_prompt_section',
]
