from __future__ import annotations
from llobot.projects import Project

class DummyProject(Project):
    """
    A project that has a name but no content.
    """
    _name: str

    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

__all__ = [
    'DummyProject',
]
