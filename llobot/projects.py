from __future__ import annotations
from datetime import datetime
import logging
import llobot.time
from llobot.knowledge import Knowledge
from llobot.knowledge.archives import KnowledgeArchive
from llobot.knowledge.sources import KnowledgeSource

_logger = logging.getLogger(__name__)

class Project:
    """
    A knowledge base, typically corresponding to a single git repository.

    Projects are the primary source of information for llobot. They are defined by a name,
    a knowledge source, and an archive for storing historical snapshots.
    """
    _name: str
    _source: KnowledgeSource
    _archive: KnowledgeArchive

    def __init__(
        self,
        name: str,
        source: KnowledgeSource,
        archive: KnowledgeArchive
    ):
        """
        Initializes a new Project.

        Args:
            name: The name of the project.
            source: The source from which to load the project's knowledge.
            archive: The archive to store snapshots of the project's knowledge.
        """
        self._name = name
        self._source = source
        self._archive = archive

    @property
    def name(self) -> str:
        """
        Project name, usually corresponding to a git repository name.
        """
        return self._name

    @property
    def source(self) -> KnowledgeSource:
        """
        The source of knowledge for this project, providing an unfiltered view.
        """
        return self._source

    @property
    def archive(self) -> KnowledgeArchive:
        """
        The archive used to store snapshots of this project.
        """
        return self._archive

    def knowledge(self, cutoff: datetime | None = None) -> Knowledge:
        """
        Retrieves the project's knowledge at a specific point in time.

        Args:
            cutoff: The timestamp to retrieve the knowledge for. If None, the latest
                    knowledge is returned.

        Returns:
            The Knowledge object representing the project state at the given cutoff.
        """
        return self.archive.last(self.name, cutoff)

    def fetch(self) -> Knowledge:
        """
        Loads the current state of the project from its source.

        Returns:
            The current Knowledge object from the source.
        """
        return self.source.load_all()

    def refresh(self):
        """
        Checks for updates from the source and archives a new snapshot if changes are found.
        """
        fresh = self.fetch()
        if fresh != self.knowledge():
            self.archive.add(self.name, llobot.time.now(), fresh)
            _logger.info(f"Refreshed: {self.name}")
        else:
            _logger.info(f"Refreshed (no change): {self.name}")

def create(
    name: str,
    source: KnowledgeSource,
    archive: KnowledgeArchive = llobot.knowledge.archives.standard()
) -> Project:
    """
    Creates a new Project instance.

    Args:
        name: The name of the project.
        source: The source from which to load the project's knowledge.
        archive: The archive to store snapshots. Defaults to the standard archive.

    Returns:
        A new Project instance.
    """
    return Project(name, source, archive)

__all__ = [
    'Project',
    'create',
]
