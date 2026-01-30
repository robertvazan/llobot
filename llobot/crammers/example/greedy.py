from __future__ import annotations
from llobot.chats.builder import ChatBuilder
from llobot.crammers.example import ExampleCrammer
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.memory import MemoryEnv
from llobot.utils.values import ValueTypeMixin

class GreedyExampleCrammer(ExampleCrammer, ValueTypeMixin):
    """
    A crammer that greedily selects the most recent examples that fit the budget.
    """
    _depth: int
    _fill: float
    _budget: int

    def __init__(self, *, depth: int = 10, fill: float = 0.5, budget: int = 50_000):
        """
        Creates a new greedy example crammer.

        Args:
            depth: Overscan depth to prevent a single large example from
                   clogging the stream and leaving a large unused budget.
            fill: Do not overscan when a reasonable fill rate is reached.
            budget: The character budget for context stuffing.
        """
        self._depth = depth
        self._fill = fill
        self._budget = budget

    def cram(self, env: Environment) -> None:
        """
        Greedily adds recent examples from memory to the context until the budget is filled.
        """
        builder = env[ContextEnv].builder
        builder.budget = builder.cost + self._budget

        examples = env[MemoryEnv].examples.recent(env)

        if builder.unused <= 0:
            return
        initial_mark = builder.mark()
        selected_examples = []
        seen_prompts = set()
        skipped = 0
        max_waste = int(builder.budget * (1 - self._fill))

        # Examples are provided most-recent-first.
        for example in examples:
            prompt_content = example[0].content
            # If there are several examples with the same prompt, include only the latest one.
            if prompt_content in seen_prompts:
                continue
            seen_prompts.add(prompt_content)

            builder.mark()
            builder.add(example)

            if builder.unused < 0:
                builder.undo()
                skipped += 1
                # Hard budget limit hit.
                if skipped > self._depth or builder.unused < max_waste:
                    break
                continue

            selected_examples.append(example)

        # Reverse to add them in chronological order.
        selected_examples.reverse()

        # We need to re-add them in the correct order.
        builder.undo(initial_mark)

        final_builder = ChatBuilder()
        for example in selected_examples:
            final_builder.add(example)

        builder.add(final_builder.build())

__all__ = [
    'GreedyExampleCrammer',
]
