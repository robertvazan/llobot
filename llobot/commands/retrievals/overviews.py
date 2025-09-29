from __future__ import annotations
from llobot.commands import Step
from llobot.environments import Environment
from llobot.environments.knowledge import KnowledgeEnv
from llobot.environments.retrievals import RetrievalsEnv
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.knowledge.subsets.standard import overviews_subset
from llobot.knowledge.trees import coerce_tree
from llobot.utils.values import ValueTypeMixin


class OverviewRetrievalStep(Step, ValueTypeMixin):
    """
    A step that adds overview documents for any already-retrieved files.

    For each document in the retrievals environment, this step finds all
    overview files in its parent directories (up to the project root) and adds
    them to the retrievals. This ensures that context for a file includes
    relevant documentation from its containing directories.
    """
    _overviews: KnowledgeSubset

    def __init__(self, *, overviews: KnowledgeSubset | None = None):
        """
        Initializes the overview retrieval step.

        Args:
            overviews: The subset defining which files are overviews.
                       Defaults to the standard one.
        """
        if overviews is None:
            overviews = overviews_subset()
        self._overviews = overviews

    def process(self, env: Environment):
        """
        Adds ancestor overview documents for all current retrievals.

        Args:
            env: The current environment.
        """
        retrievals = env[RetrievalsEnv]
        retrieved_paths = retrievals.get()
        if not retrieved_paths:
            return

        knowledge = env[KnowledgeEnv].get()
        all_overviews = knowledge & self._overviews
        overview_tree = coerce_tree(all_overviews)

        for path in retrieved_paths:
            for parent in path.parents:
                parent_tree = overview_tree[parent]
                for overview in parent_tree.file_paths:
                    retrievals.add(overview)


__all__ = [
    'OverviewRetrievalStep',
]
