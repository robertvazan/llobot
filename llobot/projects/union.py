from __future__ import annotations
from pathlib import Path
from typing import Iterable
from llobot.projects import Project
from llobot.projects.empty import EmptyProject
from llobot.projects.items import ProjectItem
from llobot.utils.values import ValueTypeMixin

class UnionProject(Project, ValueTypeMixin):
    """
    A project that is a union of several underlying projects.

    The member projects are expected to have non-overlapping prefixes. The union
    project routes method calls to the appropriate member based on path prefixes.
    """
    _projects: tuple[Project, ...]
    _routing: dict[Path, Project]

    def __init__(self, *projects: Project):
        """
        Initializes a new UnionProject.

        Args:
            *projects: A list of projects to include in the union.

        Raises:
            ValueError: If member projects have overlapping prefixes assigned to
                        different members.
        """
        flattened = []
        for p in projects:
            if isinstance(p, UnionProject):
                flattened.extend(p._projects)
            else:
                flattened.append(p)
        self._projects = tuple(flattened)

        self._routing = {}
        for p in self._projects:
            for prefix in p.prefixes:
                if prefix in self._routing and self._routing[prefix] != p:
                    raise ValueError(f"Duplicate prefix '{prefix}' in UnionProject")
                self._routing[prefix] = p

    def _ephemeral_fields(self) -> Iterable[str]:
        return ['_routing']

    @property
    def zones(self) -> set[Path]:
        all_zones = set()
        for p in self._projects:
            all_zones.update(p.zones)
        return all_zones

    @property
    def prefixes(self) -> set[Path]:
        return set(self._routing.keys())

    def _find_project(self, path: Path) -> Project | None:
        """Finds the project responsible for a given path based on the longest matching prefix."""
        for p in [path] + list(path.parents):
            if p in self._routing:
                return self._routing[p]
        return None

    def items(self, path: Path) -> list[ProjectItem]:
        project = self._find_project(path)
        return project.items(path) if project else []

    def read(self, path: Path) -> str | None:
        project = self._find_project(path)
        return project.read(path) if project else None

    def tracked(self, item: ProjectItem) -> bool:
        project = self._find_project(item.path)
        return project.tracked(item) if project else False


def union_project(*projects: Project) -> Project:
    """
    Creates a project from a list of projects.

    - If no projects are provided, returns an `EmptyProject`.
    - If one project is provided, returns that project.
    - If multiple projects are provided, returns a `UnionProject`.
    - `EmptyProject` instances are filtered out.
    """
    from llobot.projects.empty import EmptyProject
    projects = [p for p in projects if not isinstance(p, EmptyProject)]
    if not projects:
        return EmptyProject()
    if len(projects) == 1:
        return projects[0]
    return UnionProject(*projects)

__all__ = [
    'UnionProject',
    'union_project',
]
