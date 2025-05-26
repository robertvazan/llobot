from __future__ import annotations
import time
import logging
from functools import cache
from llobot.chats import ChatBranch, ChatBuilder
from llobot.models.caches import PromptStorage

_logger = logging.getLogger(__name__)

class _LastPromptStorage(PromptStorage):
    _name: str
    _timeout: float
    _prompt: ChatBranch
    _model: str
    _time: float
    _hit_chars: int
    _write_chars: int

    def __init__(self, name: str, timeout: float):
        self._name = name
        self._timeout = timeout
        self._prompt = ChatBranch()
        self._model = ''
        self._time = time.time()
        self._hit_chars = 0
        self._write_chars = 0

    @property
    def name(self) -> str:
        return self._name

    def cached(self, prompt: ChatBranch, model: str) -> ChatBranch:
        if time.time() - self._time > self._timeout:
            self.purge()
        if model != self._model:
            return ChatBranch()
        return prompt & self._prompt

    def trim(self, prompt: ChatBranch, model: str):
        if model != self._model:
            self.purge()
        self._prompt = self.cached(prompt, model)

    def write(self, prompt: ChatBranch, model: str):
        hit = self.cached(prompt, model)
        self._prompt = prompt
        self._model = model
        self._time = time.time()
        self._hit_chars += hit.cost
        self._write_chars += prompt.cost
        _logger.info(f"Prompt cache: {prompt.pretty_cost} KB ({hit.cost / prompt.cost:.0%} hit, {self._hit_chars / self._write_chars:.0%} overall) @ {self._name}")

    def purge(self):
        self._prompt = ChatBranch()

@cache
def create(name: str, timeout: float = float('inf')) -> PromptStorage:
    return _LastPromptStorage(name, timeout)

__all__ = [
    'create',
]

