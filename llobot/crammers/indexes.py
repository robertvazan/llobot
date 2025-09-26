from __future__ import annotations
from functools import cache, lru_cache
from typing import Callable
from llobot.chats.branches import ChatBranch
from llobot.knowledge import Knowledge
from llobot.knowledge.scores import KnowledgeScores
from llobot.formats.indexes import IndexFormat, standard_index_format
from llobot.formats.affirmations import affirmation_turn

class IndexCrammer:
    """
    Crammer that formats file indexes.

    Index crammers take knowledge, scores, and a budget,
    then try to fit the index or some part of it in the given budget.
    """

    def cram(self, knowledge: Knowledge, budget: int, scores: KnowledgeScores) -> ChatBranch:
        """
        Crams the index from knowledge in given budget.

        Args:
            knowledge: Knowledge to get index from.
            budget: Maximum character budget for the formatted output.
            scores: Knowledge scores, can be used to prioritize.

        Returns:
            ChatBranch containing formatted index.
        """
        return ChatBranch()

    def __call__(self, knowledge: Knowledge, budget: int, scores: KnowledgeScores) -> ChatBranch:
        return self.cram(knowledge, budget, scores)

def create_index_crammer(function: Callable[[Knowledge, int, KnowledgeScores], ChatBranch]) -> IndexCrammer:
    """
    Creates an index crammer from a function.

    Args:
        function: Cramming function that takes knowledge, budget, and scores
                  and returns a ChatBranch.

    Returns:
        IndexCrammer that uses the provided function.
    """
    class LambdaIndexCrammer(IndexCrammer):
        def cram(self, knowledge: Knowledge, budget: int, scores: KnowledgeScores) -> ChatBranch:
            return function(knowledge, budget, scores)
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
    def cram(knowledge: Knowledge, budget: int, scores: KnowledgeScores) -> ChatBranch:
        if not knowledge:
            return ChatBranch()

        # Format index
        formatted_content = index_format.render(knowledge)
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
