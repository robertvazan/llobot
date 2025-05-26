from __future__ import annotations
from functools import cache, lru_cache
from llobot.chats import ChatBranch
from llobot.contexts import Context
from llobot.scorers.history import HistoryScorer
from llobot.scorers.ranks import RankScorer
from llobot.scorers.chats import ChatScorer
import llobot.contexts
import llobot.contexts.examples
import llobot.scores.history
import llobot.scorers.history
import llobot.scorers.ranks
import llobot.scorers.chats

class ExampleCrammer:
    # Context parameter contains already assembled parts of the prompt, whether preceding or following crammer's output.
    def cram(self, streams: list[Iterable[ChatBranch]], budget: int, context: Context = llobot.contexts.empty()) -> Context:
        return llobot.contexts.empty()

def create(function: Callable[[list[Iterable[ChatBranch]], int, Context], Context]) -> ExampleCrammer:
    class LambdaExampleCrammer(ExampleCrammer):
        def cram(self, streams: list[Iterable[ChatBranch]], budget: int, context: Context = llobot.contexts.empty()) -> Context:
            return function(streams, budget, context)
    return LambdaExampleCrammer()

@cache
def greedy() -> ExampleCrammer:
    def merge(streams: list[Iterable[ChatBranch]]) -> Iterable[ChatBranch]:
        for stream in streams:
            yield from stream
    def cram(streams: list[Iterable[ChatBranch]], budget: int, context: Context = llobot.contexts.empty()) -> Context:
        context = context.examples
        examples = []
        for example in merge(streams):
            # If there are several examples with the same prompt, include only the latest one.
            if any(other[0].content == example[0].content for other in context + examples):
                continue
            if example.cost > budget:
                break
            examples.append(example)
            budget -= example.cost
        examples.reverse()
        return llobot.contexts.examples.annotate(*examples)
    return create(cram)

@lru_cache
def prioritized(
    history_scorer: HistoryScorer = llobot.scorers.history.standard(),
    scope_scorer: RankScorer = llobot.scorers.ranks.fast_with_fallback(),
    # Sorting by timestamp preserves logical dependencies between examples and thus supports in-context learning.
    sort_key: ChatScorer | None = llobot.scorers.chats.timestamp(),
    # Overscan depth to prevent single large example from clogging the stream and leaving large unused budget.
    depth: int = 10,
    # Do not overscan when we reach reasonable fill rate.
    fill: float = 0.8,
) -> ExampleCrammer:
    def cram(streams: list[Iterable[ChatBranch]], budget: int, context: Context = llobot.contexts.empty()) -> Context:
        if budget <= 0:
            return llobot.contexts.empty()
        context = context.examples
        scope_scores = scope_scorer(len(streams))
        history_scores = [scope_scores[index] * history_scorer(stream) for index, stream in enumerate(streams)]
        merged_scores = llobot.scores.history.merge(*history_scores)
        examples = []
        skipped = 0
        max_waste = int(budget * (1 - fill))
        for example in merged_scores.chats():
            # If there are several examples with the same prompt, include only the latest one.
            if any(other[0].content == example[0].content for other in context + examples):
                continue
            # Soft budget limit hit.
            if example.cost > budget:
                skipped += 1
                # Hard budget limit hit.
                if skipped > depth or budget < max_waste:
                    break
                continue
            examples.append(example)
            budget -= example.cost
        # If the sort key scorer was not provided or the sort key is not available for some chats, default to ascending score order.
        examples.reverse()
        return llobot.contexts.examples.annotate(*(sorted(examples, key=sort_key) if sort_key else examples))
    return create(cram)

@cache
def standard() -> ExampleCrammer:
    return prioritized()

@cache
def shuffled() -> ExampleCrammer:
    return prioritized(sort_key=llobot.scorers.chats.random())

__all__ = [
    'ExampleCrammer',
    'create',
    'greedy',
    'prioritized',
    'standard',
    'shuffled',
]

