"""A project library that filters keys before lookup."""
from __future__ import annotations
from pathlib import PurePosixPath
from llobot.projects import Project
from llobot.projects.library import ProjectLibrary
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.knowledge.subsets.universal import UniversalSubset
from llobot.utils.values import ValueTypeMixin
from llobot.formats.paths import coerce_path

class FilteredProjectLibrary(ProjectLibrary, ValueTypeMixin):
    """
    A project library that filters lookup keys against a whitelist.

    Keys are interpreted as relative paths and are checked against the whitelist
    before being passed to the underlying library. Invalid paths are rejected.
    A blacklisting library can be created by negating the subset.
    """
    _unfiltered: ProjectLibrary
    _whitelist: KnowledgeSubset

    def __init__(self, unfiltered: ProjectLibrary, *, whitelist: KnowledgeSubset = UniversalSubset()):
        """
        Initializes a new `FilteredProjectLibrary`.

        Args:
            unfiltered: The underlying project library to query.
            whitelist: The subset to check keys against. Defaults to matching all.
        """
        self._unfiltered = unfiltered
        self._whitelist = whitelist

    @property
    def unfiltered(self) -> ProjectLibrary:
        """The underlying project library."""
        return self._unfiltered

    @property
    def whitelist(self) -> KnowledgeSubset:
        """The subset to check keys against."""
        return self._whitelist

    def lookup(self, key: str) -> list[Project]:
        """
        Looks up projects if the key is a valid relative path and is in the whitelist.

        Args:
            key: The lookup key, interpreted as a relative path.

        Returns:
            A list of matching projects, or an empty list if the key is invalid
            or not in the whitelist.
        """
        try:
            path = coerce_path(key)
        except Exception:
            return []

        if path in self._whitelist:
            return self._unfiltered.lookup(key)
        return []

__all__ = ['FilteredProjectLibrary']
