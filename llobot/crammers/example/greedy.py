from __future__ import annotations
from typing import Iterable
from llobot.chats.thread import ChatThread
from llobot.chats.builder import ChatBuilder
from llobot.crammers.example import ExampleCrammer
from llobot.utils.values import ValueTypeMixin

class GreedyExampleCrammer(ExampleCrammer, ValueTypeMixin):
    """
    A crammer that greedily selects the most recent examples that fit the budget.
    """
    _depth: int
    _fill: float

    def __init__(self, *, depth: int = 10, fill: float = 0.5):
        """
        Creates a new greedy example crammer.

        Args:
            depth: Overscan depth to prevent a single large example from
                   clogging the stream and leaving a large unused budget.
            fill: Do not overscan when a reasonable fill rate is reached.
        """
        self._depth = depth
        self._fill = fill

    def cram(self, builder: ChatBuilder, examples: Iterable[ChatThread]) -> list[ChatThread]:
        """
        Greedily adds recent examples to the builder until the budget is filled.
        """
        if builder.unused <= 0:
            return []
        initial_mark = len(builder)
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

        return selected_examples

__all__ = [
    'GreedyExampleCrammer',
]
