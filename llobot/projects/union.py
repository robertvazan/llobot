from __future__ import annotations
from datetime import datetime
from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.archives import KnowledgeArchive
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.subsets import KnowledgeSubset, match_everything, match_nothing
from llobot.projects import Project

class UnionProject(Project):
    """
    A project that is a union of several underlying projects.
    The paths from member projects are expected to be prefixed with the project name.
    """
    _projects: list[Project]

    def __init__(self, *projects: Project):
        """
        Initializes a new UnionProject.

        Args:
            *projects: A list of projects to include in the union.
        """
        flattened = []
        for p in projects:
            if isinstance(p, UnionProject):
                flattened.extend(p._projects)
            else:
                flattened.append(p)
        self._projects = flattened

    @property
    def name(self) -> str:
        raise NotImplementedError("Union project is unnamed")

    @property
    def whitelist(self) -> KnowledgeSubset:
        return match_everything()

    @property
    def blacklist(self) -> KnowledgeSubset:
        return match_nothing()

    def list_files(self, path: Path) -> list[str]:
        results = set()
        for p in self._projects:
            results.update(p.list_files(path))
        return sorted(list(results))

    def list_subdirs(self, path: Path) -> list[str]:
        results = set()
        for p in self._projects:
            results.update(p.list_subdirs(path))
        return sorted(list(results))

    def read(self, path: Path) -> str | None:
        for p in self._projects:
            content = p.read(path)
            if content is not None:
                return content
        return None

    def enumerate(self) -> KnowledgeIndex:
        index = KnowledgeIndex()
        for p in self._projects:
            index |= p.enumerate()
        return index

    def load(self) -> Knowledge:
        knowledge = Knowledge()
        for p in self._projects:
            knowledge |= p.load()
        return knowledge

    def refresh(self, archive: KnowledgeArchive):
        for p in self._projects:
            p.refresh(archive)

    def last(self, archive: KnowledgeArchive, cutoff: datetime | None = None) -> Knowledge:
        knowledge = Knowledge()
        for p in self._projects:
            knowledge |= p.last(archive, cutoff)
        return knowledge

def union_project(*projects: Project) -> Project:
    """
    Creates a project from a list of projects.
    - If no projects are provided, returns a `NoProject`.
    - If one project is provided, returns that project.
    - If multiple projects are provided, returns a `UnionProject`.
    """
    from llobot.projects.none import NoProject
    # Filter out NoProject instances
    projects = [p for p in projects if not isinstance(p, NoProject)]
    if not projects:
        return NoProject()
    if len(projects) == 1:
        return projects[0]
    return UnionProject(*projects)

__all__ = [
    'UnionProject',
    'union_project',
]
