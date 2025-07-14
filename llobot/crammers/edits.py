from __future__ import annotations
from collections import deque
from functools import cache, lru_cache
from llobot.chats import ChatBranch
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.contexts import Context
from llobot.scorers.history import HistoryScorer
from llobot.formatters.envelopes import EnvelopeFormatter
from llobot.formatters.deletions import DeletionFormatter
from llobot.formatters.knowledge import KnowledgeFormatter
import llobot.contexts
import llobot.contexts.examples
import llobot.scores.history
import llobot.scorers.history
import llobot.formatters.envelopes
import llobot.formatters.deletions
import llobot.formatters.knowledge
import llobot.knowledge.rankings

class EditCrammer:
    """
    Crammer that combines examples with updates of documents those examples touch.
    """
    def cram(self, examples: Iterable[ChatBranch], knowledge: Knowledge, budget: int) -> Context:
        return llobot.contexts.empty()

    def __call__(self, examples: Iterable[ChatBranch], knowledge: Knowledge, budget: int) -> Context:
        return self.cram(examples, knowledge, budget)

def create(function: Callable[[Iterable[ChatBranch], Knowledge, int], Context]) -> EditCrammer:
    class LambdaEditCrammer(EditCrammer):
        def cram(self, examples: Iterable[ChatBranch], knowledge: Knowledge, budget: int) -> Context:
            return function(examples, knowledge, budget)
    return LambdaEditCrammer()

@lru_cache
def prioritized(
    history_scorer: HistoryScorer = llobot.scorers.history.standard(),
    update_formatter: KnowledgeFormatter = llobot.formatters.knowledge.updates(),
    deletion_formatter: DeletionFormatter = llobot.formatters.deletions.standard(),
    parser: EnvelopeFormatter = llobot.formatters.envelopes.standard(),
    # Overscan depth to prevent single large example from clogging the stream and leaving large unused budget.
    depth: int = 10,
    # Do not overscan when we reach reasonable fill rate.
    fill: float = 0.8,
) -> EditCrammer:
    """
    Creates an edit crammer that prioritizes examples and includes document updates.

    The crammer builds the result from the end to the beginning, one example at a time.
    For each example, it appends fresh versions of documents the example has touched
    unless those documents have been already added earlier or the documents as present
    in the example are identical to their fresh version.
    """
    def cram(examples: Iterable[ChatBranch], knowledge: Knowledge, budget: int) -> Context:
        chunks = []
        seen_prompts = set()
        seen_paths = set()
        skipped = 0
        max_waste = int(budget * (1 - fill))

        for example in history_scorer(examples).chats():
            # If there are several examples with the same prompt, include only the latest one.
            if not example:
                continue
            if example[0].content in seen_prompts:
                continue
            seen_prompts.add(example[0].content)

            example_context = llobot.contexts.examples.annotate(example, parser=parser)
            example_knowledge = example_context.knowledge

            deletion_buffer = set()
            update_buffer = {}
            for path, content in example_knowledge:
                if path in seen_paths:
                    continue
                if path not in knowledge:
                    deletion_buffer.add(path)
                elif knowledge[path] != content:
                    update_buffer[path] = knowledge[path]
            deletions = KnowledgeIndex(deletion_buffer)
            updates = Knowledge(update_buffer)

            deletion_context = deletion_formatter(deletions)
            update_context = update_formatter(updates, llobot.knowledge.rankings.lexicographical(updates))
            chunk = llobot.contexts.compose(example_context, deletion_context, update_context)

            if chunk.cost > budget:
                skipped += 1
                if skipped > depth or budget < max_waste:
                    break
                continue

            chunks.append(chunk)
            budget -= chunk.cost
            seen_paths.update(example_knowledge.keys())

        chunks.reverse()
        return llobot.contexts.compose(*chunks)

    return create(cram)

@cache
def standard() -> EditCrammer:
    return prioritized()

__all__ = [
    'EditCrammer',
    'create',
    'prioritized',
    'standard',
]

