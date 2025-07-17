from __future__ import annotations
from functools import cache, lru_cache
from llobot.chats import ChatBranch, ChatBuilder
from llobot.scorers.history import HistoryScorer
from llobot.formatters.envelopes import EnvelopeFormatter
import llobot.scores.history
import llobot.scorers.history
import llobot.formatters.envelopes

class ExampleCrammer:
    def cram(self, examples: Iterable[ChatBranch], budget: int) -> ChatBranch:
        return ChatBranch()

    def __call__(self, examples: Iterable[ChatBranch], budget: int) -> ChatBranch:
        return self.cram(examples, budget)

def create(function: Callable[[Iterable[ChatBranch], int], ChatBranch]) -> ExampleCrammer:
    class LambdaExampleCrammer(ExampleCrammer):
        def cram(self, examples: Iterable[ChatBranch], budget: int) -> ChatBranch:
            return function(examples, budget)
    return LambdaExampleCrammer()

@lru_cache
def greedy(parser: EnvelopeFormatter = llobot.formatters.envelopes.standard()) -> ExampleCrammer:
    def cram(examples: Iterable[ChatBranch], budget: int) -> ChatBranch:
        selected_examples = []
        seen_prompts = set()
        for example in examples:
            prompt_content = example[0].content
            # If there are several examples with the same prompt, include only the latest one.
            if prompt_content in seen_prompts:
                continue
            if example.cost > budget:
                break
            selected_examples.append(example)
            seen_prompts.add(prompt_content)
            budget -= example.cost
        selected_examples.reverse()
        chat = ChatBuilder()
        for example in selected_examples:
            chat.add(example)
        return chat.build()
    return create(cram)

@lru_cache
def prioritized(
    history_scorer: HistoryScorer = llobot.scorers.history.standard(),
    # Overscan depth to prevent single large example from clogging the stream and leaving large unused budget.
    depth: int = 10,
    # Do not overscan when we reach reasonable fill rate.
    fill: float = 0.8,
    parser: EnvelopeFormatter = llobot.formatters.envelopes.standard(),
) -> ExampleCrammer:
    def cram(examples: Iterable[ChatBranch], budget: int) -> ChatBranch:
        if budget <= 0:
            return ChatBranch()
        history_scores = history_scorer(examples)
        selected_examples = []
        seen_prompts = set()
        skipped = 0
        max_waste = int(budget * (1 - fill))
        for example in history_scores.chats():
            prompt_content = example[0].content
            # If there are several examples with the same prompt, include only the latest one.
            if prompt_content in seen_prompts:
                continue
            # Soft budget limit hit.
            if example.cost > budget:
                skipped += 1
                # Hard budget limit hit.
                if skipped > depth or budget < max_waste:
                    break
                continue
            selected_examples.append(example)
            seen_prompts.add(prompt_content)
            budget -= example.cost
        selected_examples.reverse()
        chat = ChatBuilder()
        for example in selected_examples:
            chat.add(example)
        return chat.build()
    return create(cram)

@cache
def standard() -> ExampleCrammer:
    return prioritized()

__all__ = [
    'ExampleCrammer',
    'create',
    'greedy',
    'prioritized',
    'standard',
]
