from __future__ import annotations
from datetime import datetime
from llobot.knowledge import Knowledge
from llobot.knowledge.archives import KnowledgeArchive
from llobot.projects import Project

class NoProject(Project):
    """
    A project that represents the absence of a project.
    """
    @property
    def name(self) -> str:
        """
        The name of the project. Throws, as no-project is unnamed.
        """
        raise NotImplementedError("No project is selected")

    def __eq__(self, other: object) -> bool:
        return isinstance(other, NoProject)

    def refresh(self, archive: KnowledgeArchive):
        """A no-op refresh for no project."""
        pass

    def last(self, archive: KnowledgeArchive, cutoff: datetime | None = None) -> Knowledge:
        """Returns empty knowledge for no project."""
        return Knowledge()

__all__ = [
    'NoProject',
]
