from __future__ import annotations
from functools import cache, lru_cache
from typing import Callable
from llobot.chats.branches import ChatBranch
from llobot.chats.intents import ChatIntent
from llobot.chats.messages import ChatMessage
from llobot.knowledge.scores import KnowledgeScores
from llobot.knowledge.trees import standard_tree
from llobot.formats.indexes import IndexFormat, standard_index_format
from llobot.formats.affirmations import affirmation_turn

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

def create_index_crammer(function: Callable[[KnowledgeScores, int], ChatBranch]) -> IndexCrammer:
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
def optional_index_crammer(
    index_format: IndexFormat = standard_index_format(),
) -> IndexCrammer:
    """
    Creates an index crammer that includes the full index or nothing.

    This crammer formats the entire index using the specified
    index format. If the formatted index fits within the budget, it returns it
    wrapped in a ChatBranch. Otherwise, it returns an empty ChatBranch.

    Args:
        index_format: Formatter to use for rendering the index.

    Returns:
        IndexCrammer that includes all files or none.
    """
    def cram(scores: KnowledgeScores, budget: int) -> ChatBranch:
        if not scores:
            return ChatBranch()

        # Get index from scores
        index = scores.keys()

        # Format index
        formatted_content = index_format.render(index)
        if not formatted_content:
            return ChatBranch()

        # Check if it fits in budget
        result = affirmation_turn(formatted_content)

        if result.cost <= budget:
            return result
        else:
            return ChatBranch()

    return create_index_crammer(cram)

@cache
def standard_index_crammer() -> IndexCrammer:
    """
    Returns the standard index crammer.

    Returns:
        The default IndexCrammer (currently optional with standard index format).
    """
    return optional_index_crammer()

__all__ = [
    'IndexCrammer',
    'create_index_crammer',
    'optional_index_crammer',
    'standard_index_crammer',
]
