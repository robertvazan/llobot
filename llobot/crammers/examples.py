from __future__ import annotations
from functools import cache, lru_cache
from llobot.chats import ChatBranch
from llobot.contexts import Context
from llobot.scorers.history import HistoryScorer
from llobot.scorers.chats import ChatScorer
from llobot.formatters.envelopes import EnvelopeFormatter
import llobot.contexts
import llobot.contexts.examples
import llobot.scores.history
import llobot.scorers.history
import llobot.scorers.chats
import llobot.formatters.envelopes

class ExampleCrammer:
    # Context parameter contains already assembled parts of the prompt, whether preceding or following crammer's output.
    def cram(self, examples: Iterable[ChatBranch], budget: int, context: Context = llobot.contexts.empty()) -> Context:
        return llobot.contexts.empty()

def create(function: Callable[[Iterable[ChatBranch], int, Context], Context]) -> ExampleCrammer:
    class LambdaExampleCrammer(ExampleCrammer):
        def cram(self, examples: Iterable[ChatBranch], budget: int, context: Context = llobot.contexts.empty()) -> Context:
            return function(examples, budget, context)
    return LambdaExampleCrammer()

@lru_cache
def greedy(parser: EnvelopeFormatter = llobot.formatters.envelopes.standard()) -> ExampleCrammer:
    def cram(examples: Iterable[ChatBranch], budget: int, context: Context = llobot.contexts.empty()) -> Context:
        context_examples = context.examples
        selected_examples = []
        for example in examples:
            # If there are several examples with the same prompt, include only the latest one.
            if any(other[0].content == example[0].content for other in context_examples + selected_examples):
                continue
            if example.cost > budget:
                break
            selected_examples.append(example)
            budget -= example.cost
        selected_examples.reverse()
        return llobot.contexts.examples.annotate(*selected_examples, parser=parser)
    return create(cram)

@lru_cache
def prioritized(
    history_scorer: HistoryScorer = llobot.scorers.history.standard(),
    # Sorting by timestamp preserves logical dependencies between examples and thus supports in-context learning.
    sort_key: ChatScorer | None = llobot.scorers.chats.timestamp(),
    # Overscan depth to prevent single large example from clogging the stream and leaving large unused budget.
    depth: int = 10,
    # Do not overscan when we reach reasonable fill rate.
    fill: float = 0.8,
    parser: EnvelopeFormatter = llobot.formatters.envelopes.standard(),
) -> ExampleCrammer:
    def cram(examples: Iterable[ChatBranch], budget: int, context: Context = llobot.contexts.empty()) -> Context:
        if budget <= 0:
            return llobot.contexts.empty()
        context_examples = context.examples
        history_scores = history_scorer(examples)
        selected_examples = []
        skipped = 0
        max_waste = int(budget * (1 - fill))
        for example in history_scores.chats():
            # If there are several examples with the same prompt, include only the latest one.
            if any(other[0].content == example[0].content for other in context_examples + selected_examples):
                continue
            # Soft budget limit hit.
            if example.cost > budget:
                skipped += 1
                # Hard budget limit hit.
                if skipped > depth or budget < max_waste:
                    break
                continue
            selected_examples.append(example)
            budget -= example.cost
        # If the sort key scorer was not provided or the sort key is not available for some chats, default to ascending score order.
        selected_examples.reverse()
        return llobot.contexts.examples.annotate(*(sorted(selected_examples, key=sort_key) if sort_key else selected_examples), parser=parser)
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

