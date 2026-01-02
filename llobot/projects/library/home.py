"""A project library that finds projects in a home directory."""
from __future__ import annotations

from pathlib import Path, PurePosixPath

from llobot.formats.paths import coerce_path
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.projects import Project
from llobot.projects.directory import DirectoryProject
from llobot.projects.library import ProjectLibrary
from llobot.projects.shallow import ShallowProject
from llobot.utils.values import ValueTypeMixin


class HomeProjectLibrary(ProjectLibrary, ValueTypeMixin):
    """
    A project library that interprets keys as relative paths to projects
    under a configured home directory.

    If a directory exists at `home / key`, this library returns a corresponding
    `DirectoryProject`.

    Defaults
    --------
    - Prefix defaults to the same home-relative computation as in
      `DirectoryProject`, but with a different fallback: when the
      home-relative computation cannot be used, the fallback equals the lookup
      key.
    """
    _home: Path
    _whitelist: KnowledgeSubset | None
    _blacklist: KnowledgeSubset | None
    _mutable: bool
    _parents: bool

    def __init__(
        self,
        home: str | Path = '~',
        *,
        whitelist: KnowledgeSubset | None = None,
        blacklist: KnowledgeSubset | None = None,
        mutable: bool = False,
        parents: bool = True,
    ):
        """
        Initializes a new `HomeProjectLibrary`.

        Args:
            home: The base directory to look for projects in. Defaults to `~`.
            whitelist: A whitelist to pass to created `DirectoryProject` instances.
            blacklist: A blacklist to pass to created `DirectoryProject` instances.
            mutable: If `True`, created projects allow write operations.
            parents: If `True`, the library also returns shallow projects for
                ancestor directories of any matched project. Defaults to `True`.
        """
        self._home = Path(home).expanduser().absolute()
        self._whitelist = whitelist
        self._blacklist = blacklist
        self._mutable = mutable
        self._parents = parents

    def _default_prefix(self, directory: Path, zone: PurePosixPath) -> PurePosixPath:
        """
        Computes default prefix similarly to `DirectoryProject`, but with
        fallback equal to the provided key.
        """
        home = Path.home()
        if directory.is_relative_to(home):
            relative = directory.relative_to(home)
            # Avoid '.', which would be rejected by validate_zone().
            if relative != Path('.') and relative.parts:
                try:
                    return coerce_path(relative)
                except ValueError:
                    # Fall back to key below.
                    pass
        return zone

    def _project(self, directory: Path, zone: PurePosixPath) -> DirectoryProject:
        """
        Constructs a directory project with HomeProjectLibrary defaults.
        """
        return DirectoryProject(
            directory,
            prefix=self._default_prefix(directory, zone),
            whitelist=self._whitelist,
            blacklist=self._blacklist,
            mutable=self._mutable,
        )

    def lookup(self, key: str) -> list[Project]:
        """
        Looks for a directory project at `key` relative to the library home directory.

        Args:
            key: The lookup key, interpreted as a relative path.

        Returns:
            A list containing a `DirectoryProject` for the matched path. If
            `parents` is `True`, the list will also include `ShallowProject`
            wrappers for all parent directories (up to the library home).
            Returns an empty list if no directory is found.
        """
        try:
            zone = coerce_path(key)
        except Exception:
            return []

        project_dir = (self._home / zone).absolute()
        if not project_dir.is_dir():
            return []

        projects: list[Project] = [self._project(project_dir, zone)]

        if self._parents:
            current = zone
            while current.parent != PurePosixPath('.'):
                current = current.parent
                parent_dir = (self._home / current).absolute()
                if not parent_dir.is_dir():
                    break
                projects.append(ShallowProject(self._project(parent_dir, current)))

        return projects


__all__ = ['HomeProjectLibrary']
