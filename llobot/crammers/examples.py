from __future__ import annotations
from functools import cache, lru_cache
from llobot.chats.branches import ChatBranch
from llobot.chats.builders import ChatBuilder

class ExampleCrammer:
    def cram(self, examples: Iterable[ChatBranch], budget: int) -> ChatBranch:
        return ChatBranch()

    def __call__(self, examples: Iterable[ChatBranch], budget: int) -> ChatBranch:
        return self.cram(examples, budget)

def create_example_crammer(function: Callable[[Iterable[ChatBranch], int], ChatBranch]) -> ExampleCrammer:
    class LambdaExampleCrammer(ExampleCrammer):
        def cram(self, examples: Iterable[ChatBranch], budget: int) -> ChatBranch:
            return function(examples, budget)
    return LambdaExampleCrammer()

@lru_cache
def greedy_example_crammer(
    # Overscan depth to prevent single large example from clogging the stream and leaving large unused budget.
    depth: int = 10,
    # Do not overscan when we reach reasonable fill rate.
    fill: float = 0.5,
) -> ExampleCrammer:
    def cram(examples: Iterable[ChatBranch], budget: int) -> ChatBranch:
        if budget <= 0:
            return ChatBranch()
        selected_examples = []
        seen_prompts = set()
        skipped = 0
        max_waste = int(budget * (1 - fill))
        for example in examples:
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
    return create_example_crammer(cram)

@cache
def standard_example_crammer() -> ExampleCrammer:
    return greedy_example_crammer()

__all__ = [
    'ExampleCrammer',
    'create_example_crammer',
    'greedy_example_crammer',
    'standard_example_crammer',
]
