"""A project library that finds projects in a home directory."""
from __future__ import annotations
from pathlib import Path
from llobot.projects import Project
from llobot.projects.directory import DirectoryProject
from llobot.projects.library import ProjectLibrary
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.utils.values import ValueTypeMixin

class HomeProjectLibrary(ProjectLibrary, ValueTypeMixin):
    """
    A project library that interprets keys as relative paths to projects
    in a home directory, creating `DirectoryProject` instances for existing
    directories.
    """
    _home: Path
    _whitelist: KnowledgeSubset | None
    _blacklist: KnowledgeSubset | None
    _mutable: bool

    def __init__(self,
        home: str | Path = '~',
        *,
        whitelist: KnowledgeSubset | None = None,
        blacklist: KnowledgeSubset | None = None,
        mutable: bool = False
    ):
        """
        Initializes a new `HomeProjectLibrary`.

        Args:
            home: The base directory to look for projects in. Defaults to `~`.
            whitelist: A whitelist to pass to created `DirectoryProject`s.
            blacklist: A blacklist to pass to created `DirectoryProject`s.
            mutable: If `True`, created projects allow write operations.
        """
        self._home = Path(home).expanduser().absolute()
        self._whitelist = whitelist
        self._blacklist = blacklist
        self._mutable = mutable

    def lookup(self, key: str) -> list[Project]:
        """
        Looks for a directory project at `key` relative to the home directory.

        If a directory exists at `home / key`, a `DirectoryProject` is returned
        for it. The project's prefix is set to `key`.

        Args:
            key: The lookup key, interpreted as a relative path.

        Returns:
            A list containing one `DirectoryProject` if found, or an empty list.
        """
        try:
            path = Path(key)
            if path.is_absolute() or '..' in path.parts:
                return []
        except Exception:
            return []

        project_dir = self._home / path
        if project_dir.is_dir():
            return [DirectoryProject(
                project_dir,
                prefix=key,
                whitelist=self._whitelist,
                blacklist=self._blacklist,
                mutable=self._mutable
            )]
        return []

__all__ = ['HomeProjectLibrary']
