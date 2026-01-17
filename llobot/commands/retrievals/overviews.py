from __future__ import annotations
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.knowledge import KnowledgeEnv
from llobot.environments.retrievals import RetrievalsEnv
from llobot.formats.knowledge import KnowledgeFormat, standard_knowledge_format
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.knowledge.subsets.standard import overviews_subset
from llobot.knowledge.trees import coerce_tree


def assume_overview_retrieval_commands(
    env: Environment,
    *,
    overviews: KnowledgeSubset | None = None,
    knowledge_format: KnowledgeFormat | None = None,
):
    """
    Adds overview documents for any already-retrieved files.

    For each document in the retrievals environment, this function finds all
    overview files in its parent directories (up to the project root) and adds
    them to the retrievals. This ensures that context for a file includes
    relevant documentation from its containing directories.

    Args:
        env: The current environment.
        overviews: The subset defining which files are overviews.
            Defaults to the standard one.
        knowledge_format: The format to use for checking duplicates.
            Defaults to the standard format.
    """
    if overviews is None:
        overviews = overviews_subset()

    retrievals = env[RetrievalsEnv]
    retrieved_paths = retrievals.get()
    if not retrieved_paths:
        return

    knowledge = env[KnowledgeEnv].get()
    all_overviews = knowledge & overviews
    overview_tree = coerce_tree(all_overviews)

    newly_added = set()
    current_retrievals = retrievals.get()

    for path in retrieved_paths:
        for parent in path.parents:
            parent_tree = overview_tree[parent]
            for overview in parent_tree.file_paths:
                if overview not in current_retrievals and overview not in newly_added:
                    retrievals.add(overview)
                    newly_added.add(overview)

    if newly_added:
        if knowledge_format is None:
            knowledge_format = standard_knowledge_format()

        context = env[ContextEnv].build()
        files_to_report = []
        for path in sorted(newly_added):
            formatted = knowledge_format.document_format.render(path, knowledge[path])
            if not any(formatted in msg.content for msg in context):
                files_to_report.append(path)

        if files_to_report:
            lines = ["Reading also related files:"] + [f"- `~/{p}`" for p in files_to_report]
            env[ContextEnv].add(ChatMessage(ChatIntent.SYSTEM, "\n".join(lines)))


__all__ = [
    'assume_overview_retrieval_commands',
]
