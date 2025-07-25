from __future__ import annotations
from collections import deque
from functools import cache, lru_cache
from llobot.chats import ChatBranch, ChatBuilder
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.deltas import DocumentDelta, KnowledgeDeltaBuilder
from llobot.formatters.envelopes import EnvelopeFormatter
from llobot.formatters.knowledge import KnowledgeFormatter
import llobot.formatters.envelopes
import llobot.formatters.knowledge
import llobot.knowledge.rankings
import llobot.knowledge.deltas

class EditCrammer:
    """
    Crammer that combines examples with updates of documents those examples touch.
    """
    def cram(self, examples: Iterable[ChatBranch], knowledge: Knowledge, budget: int) -> tuple[ChatBranch, KnowledgeIndex]:
        return ChatBranch(), KnowledgeIndex()

    def __call__(self, examples: Iterable[ChatBranch], knowledge: Knowledge, budget: int) -> tuple[ChatBranch, KnowledgeIndex]:
        return self.cram(examples, knowledge, budget)

def create(function: Callable[[Iterable[ChatBranch], Knowledge, int], tuple[ChatBranch, KnowledgeIndex]]) -> EditCrammer:
    class LambdaEditCrammer(EditCrammer):
        def cram(self, examples: Iterable[ChatBranch], knowledge: Knowledge, budget: int) -> tuple[ChatBranch, KnowledgeIndex]:
            return function(examples, knowledge, budget)
    return LambdaEditCrammer()

@lru_cache
def greedy(
    envelopes: EnvelopeFormatter = llobot.formatters.envelopes.standard(),
    knowledge_formatter: KnowledgeFormatter = llobot.formatters.knowledge.standard(),
    # Overscan depth to prevent single large example from clogging the stream and leaving large unused budget.
    depth: int = 10,
    # Do not keep looking for old examples when we reach reasonable fill rate.
    fill: float = 0.5,
) -> EditCrammer:
    """
    Creates an edit crammer that processes examples and includes document updates.

    The crammer builds the result from the end to the beginning, one example at a time.
    For each example, it appends fresh versions of documents the example has touched
    unless those documents have been already added earlier or the documents as present
    in the example are identical to their fresh version.
    """
    def cram(examples: Iterable[ChatBranch], knowledge: Knowledge, budget: int) -> tuple[ChatBranch, KnowledgeIndex]:
        chunks = []
        seen_prompts = set()
        updated_paths = set()
        touched_paths = set()
        skipped = 0
        max_waste = int(budget * (1 - fill))

        for example in examples:
            # If there are several examples with the same prompt, include only the latest one.
            if not example or example[0].content in seen_prompts:
                continue
            seen_prompts.add(example[0].content)

            example_delta = envelopes.parse_chat(example)
            example_full = example_delta.full

            update_builder = llobot.knowledge.deltas.KnowledgeDeltaBuilder()

            # Check for deletions
            for path in example_delta.present:
                if path not in knowledge and path not in updated_paths:
                    update_builder.add(DocumentDelta(path, None, removed=True))

            # Check for modifications
            for path in example_delta.touched:
                if path in knowledge and path not in updated_paths:
                    if path not in example_full or example_full[path] != knowledge[path]:
                         update_builder.add(DocumentDelta(path, knowledge[path], modified=True))

            update_delta = update_builder.build()
            update_chat = knowledge_formatter.render(update_delta)

            chunk_chat = example + update_chat

            if chunk_chat.cost > budget:
                skipped += 1
                if skipped > depth or budget < max_waste:
                    break
                continue

            chunks.append(chunk_chat)
            budget -= chunk_chat.cost
            updated_paths.update(update_delta.touched)
            touched_paths.update(example_delta.touched)
            touched_paths.update(update_delta.touched)

        chunks.reverse()
        result = ChatBuilder()
        for chunk in chunks:
            result.add(chunk)
        return result.build(), KnowledgeIndex(touched_paths)

    return create(cram)

@cache
def standard() -> EditCrammer:
    return greedy()

__all__ = [
    'EditCrammer',
    'create',
    'greedy',
    'standard',
]
