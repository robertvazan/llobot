from __future__ import annotations
from datetime import datetime
from pathlib import Path
import logging
import llobot.time
from llobot.knowledge import Knowledge
from llobot.knowledge.archives import KnowledgeArchive
from llobot.knowledge.subsets import KnowledgeSubset
import llobot.knowledge.subsets
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.sources import KnowledgeSource

_logger = logging.getLogger(__name__)

# Project usually corresponds to single git repository or a directory of related files.
class Project:
    _name: str
    _subset: KnowledgeSubset
    _root: Project
    _subprojects: list[Project]
    _source: KnowledgeSource
    _archive: KnowledgeArchive

    def __init__(
        self,
        name: str,
        source: KnowledgeSource,
        archive: KnowledgeArchive,
        subset: KnowledgeSubset = llobot.knowledge.subsets.everything(),
        root: Project | None = None
    ):
        self._name = name
        self._subset = subset
        self._root = root or self
        self._subprojects = []
        self._source = source
        self._archive = archive

    # Project name, usually corresponding to git repository name.
    @property
    def name(self) -> str:
        return self._name

    @property
    def subset(self) -> KnowledgeSubset:
        return self._subset

    @property
    def root(self) -> Project:
        return self._root

    @property
    def subprojects(self) -> list[Project]:
        return self._subprojects

    # This should be mostly unfiltered fetch of the whole project.
    @property
    def source(self) -> KnowledgeSource:
        return self._source

    # Archive used to store snapshots of this project.
    @property
    def archive(self) -> KnowledgeArchive:
        return self._archive

    def add_subproject(self, subproject: Project):
        self._subprojects.append(subproject)

    def find(self, name: str) -> Project | None:
        if self.name == name:
            return self
        for subproject in self.subprojects:
            if subproject.name == name:
                return subproject
        return None

    def knowledge(self, cutoff: datetime | None = None) -> Knowledge:
        return self.archive.last(self.root.name, cutoff) & self.subset

    def fetch(self) -> Knowledge:
        return self.source.load_all()

    def refresh(self):
        if self is not self.root:
            return self.root.refresh()

        fresh = self.fetch()
        if fresh != self.knowledge():
            self.archive.add(self.name, llobot.time.now(), fresh)
            _logger.info(f"Refreshed: {self.name}")
        else:
            _logger.info(f"Refreshed (no change): {self.name}")

def create(
    name: str,
    source: KnowledgeSource,
    archive: KnowledgeArchive = llobot.knowledge.archives.standard(),
    subprojects: dict[str, KnowledgeSubset | KnowledgeIndex | Path | str] = {}
) -> Project:
    root = Project(name, source, archive)

    for subproject_name, subset_spec in subprojects.items():
        # If the name starts with a dash, it is appended to the root project name
        if subproject_name.startswith('-'):
            full_name = name + subproject_name
        else:
            full_name = subproject_name

        subset = llobot.knowledge.subsets.coerce(subset_spec)
        subproject = Project(full_name, root.source, root.archive, subset, root)
        root.add_subproject(subproject)

    return root

__all__ = [
    'Project',
    'create',
]

