from __future__ import annotations
from pathlib import PurePosixPath
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
    _routing: dict[PurePosixPath, Project]

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
    def prefixes(self) -> set[PurePosixPath]:
        return set(self._routing.keys())

    @property
    def summary(self) -> list[str]:
        result = []
        for p in self._projects:
            result.extend(p.summary)
        return result

    def _find_project(self, path: PurePosixPath) -> Project | None:
        """Finds the project responsible for a given path based on the longest matching prefix."""
        for p in [path] + list(path.parents):
            if p in self._routing:
                return self._routing[p]
        return None

    def items(self, path: PurePosixPath) -> list[ProjectItem]:
        project = self._find_project(path)
        return project.items(path) if project else []

    def read(self, path: PurePosixPath) -> str | None:
        project = self._find_project(path)
        return project.read(path) if project else None

    def tracked(self, item: ProjectItem) -> bool:
        project = self._find_project(item.path)
        return project.tracked(item) if project else False

    def mutable(self, path: PurePosixPath) -> bool:
        """
        Checks if a path is mutable by delegating to the appropriate member project.
        """
        project = self._find_project(path)
        return project.mutable(path) if project else False

    def write(self, path: PurePosixPath, content: str):
        """
        Writes to a file by delegating to the appropriate member project.
        """
        if not self.mutable(path):
            raise PermissionError(f"Path is not mutable: {path}")
        project = self._find_project(path)
        # There must be a project if mutable() succeeded.
        assert project, f"Path {path} is mutable but has no project."
        project.write(path, content)

    def remove(self, path: PurePosixPath):
        """
        Removes a file by delegating to the appropriate member project.
        """
        if not self.mutable(path):
            raise PermissionError(f"Path is not mutable: {path}")
        project = self._find_project(path)
        # There must be a project if mutable() succeeded.
        assert project, f"Path {path} is mutable but has no project."
        project.remove(path)

    def move(self, source: PurePosixPath, destination: PurePosixPath):
        """
        Moves a file from a source path to a destination path.

        If both source and destination are handled by the same member project,
        the move is delegated to that project. Otherwise, it falls back to a
        read-write-remove sequence.

        Args:
            source: The path of the file to move.
            destination: The new path for the file.

        Raises:
            PermissionError: If the source is not readable/removable or the
                             destination is not writable.
            FileNotFoundError: If the source file does not exist or is not a file.
        """
        source_project = self._find_project(source)
        destination_project = self._find_project(destination)

        if source_project and source_project is destination_project:
            source_project.move(source, destination)
        else:
            # Fallback to base implementation for cross-project moves
            super().move(source, destination)


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
