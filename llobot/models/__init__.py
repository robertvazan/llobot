from __future__ import annotations
from typing import Iterable
from llobot.chats.branches import ChatBranch
from llobot.text import dashed_name

class Model:
    # Name must be globally unique, something like ollama/model-name:tag.
    # Model name should not include endpoint, because every sane setup will access given model only over single path.
    @property
    def name(self) -> str:
        raise NotImplementedError

    @property
    def dashed_name(self) -> str:
        return dashed_name(self.name)

    # Shorter names that are not necessarily unique.
    @property
    def aliases(self) -> Iterable[str]:
        return []

    def __str__(self) -> str:
        return self.name

    # Options should be a flat dict with string keys and JSON-serializable values (str, int, float, bool).
    @property
    def options(self) -> dict:
        return {}

    # Raises an exception on unexpected options or unexpected option values.
    def validate_options(self, options: dict):
        pass

    # Coerces the options and merges them with defaults, producing a new model that has the merged options as its defaults.
    # Uncoerced options can have string values, empty on None values for clearing, invalid values, and extraneous keys.
    def configure(self, options: dict) -> Model:
        return self

    # Number of characters to use for context stuffing. This is a cost-benefit decision rather than an inherent model limit.
    @property
    def context_budget(self) -> int:
        return 0

    def generate(self, prompt: ChatBranch) -> 'ModelStream':
        raise NotImplementedError

def echo_model(*, context_budget: int = 100_000, aliases: Iterable[str] = []) -> Model:
    from llobot.models.streams import ModelStream, text_stream
    class EchoModel(Model):
        _context_budget: int
        def __init__(self, context_budget: int):
            self._context_budget = context_budget
        @property
        def name(self) -> str:
            return 'echo'
        @property
        def aliases(self) -> Iterable[str]:
            yield f'echo:{self._context_budget // 1024}k'
            yield from aliases
        @property
        def options(self) -> dict:
            return {
                'context_budget': self._context_budget,
            }
        def validate_options(self, options: dict):
            allowed = {'context_budget'}
            for unrecognized in set(options) - allowed:
                raise ValueError(f"Unrecognized option: {unrecognized}")
        def configure(self, options: dict) -> Model:
            return EchoModel(
                int(options.get('context_budget', self._context_budget)),
            )
        @property
        def context_budget(self) -> int:
            return self._context_budget
        def generate(self, prompt: ChatBranch) -> ModelStream:
            return text_stream(prompt.monolithic())
    return EchoModel(context_budget)

__all__ = [
    'Model',
    'echo_model',
]
