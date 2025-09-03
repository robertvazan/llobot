from __future__ import annotations
from functools import cache, lru_cache
from llobot.chats.branches import ChatBranch
from llobot.chats.builders import ChatBuilder
from llobot.chats.intents import ChatIntent
from llobot.chats.messages import ChatMessage
from llobot.knowledge.scores import KnowledgeScores
from llobot.knowledge.trees import KnowledgeTree
from llobot.formatters.trees import TreeFormatter
import llobot.knowledge.trees
import llobot.formatters.trees

class IndexCrammer:
    """
    Crammer that formats file indexes.

    Index crammers take knowledge scores (which define the index through their keys) and a budget,
    then try to fit the index or some part of it in the given budget.
    """

    def cram(self, scores: KnowledgeScores, budget: int) -> ChatBranch:
        """
        Crams the index from score keys in given budget.

        Args:
            scores: Knowledge scores whose keys define the index to cram.
            budget: Maximum character budget for the formatted output.

        Returns:
            ChatBranch containing formatted index.
        """
        return ChatBranch()

    def __call__(self, scores: KnowledgeScores, budget: int) -> ChatBranch:
        return self.cram(scores, budget)

def create(function: Callable[[KnowledgeScores, int], ChatBranch]) -> IndexCrammer:
    """
    Creates an index crammer from a function.

    Args:
        function: Cramming function that takes scores and budget and returns a ChatBranch.

    Returns:
        IndexCrammer that uses the provided function.
    """
    class LambdaIndexCrammer(IndexCrammer):
        def cram(self, scores: KnowledgeScores, budget: int) -> ChatBranch:
            return function(scores, budget)
    return LambdaIndexCrammer()

@lru_cache
def optional(
    tree_formatter: TreeFormatter = llobot.formatters.trees.standard("Project files"),
    affirmation: str = 'I see.',
) -> IndexCrammer:
    """
    Creates an index crammer that includes the full tree or nothing.

    This crammer formats the entire index as a directory tree using the specified
    tree formatter. If the formatted tree fits within the budget, it returns it
    wrapped in a ChatBranch. Otherwise, it returns an empty ChatBranch.

    Args:
        tree_formatter: Formatter to use for rendering the directory tree.

    Returns:
        IndexCrammer that includes all files or none.
    """
    def cram(scores: KnowledgeScores, budget: int) -> ChatBranch:
        if not scores:
            return ChatBranch()

        # Create tree from index
        index = scores.keys()
        tree = llobot.knowledge.trees.standard(index)

        # Format tree
        formatted_content = tree_formatter(tree)
        if not formatted_content:
            return ChatBranch()

        # Check if it fits in budget
        chat = ChatBuilder()
        chat.add(ChatMessage(ChatIntent.SYSTEM, formatted_content))
        chat.add(ChatMessage(ChatIntent.AFFIRMATION, affirmation))
        result = chat.build()

        if result.cost <= budget:
            return result
        else:
            return ChatBranch()

    return create(cram)

@cache
def standard() -> IndexCrammer:
    """
    Returns the standard index crammer.

    Returns:
        The default IndexCrammer (currently optional with standard tree formatter).
    """
    return optional()

__all__ = [
    'IndexCrammer',
    'create',
    'optional',
    'standard',
]
