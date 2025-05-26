from __future__ import annotations
import time
import logging
from collections import defaultdict
from functools import cache
from llobot.chats import ChatBranch
from llobot.models.caches import PromptStorage

_logger = logging.getLogger(__name__)

class _LruPromptStorage(PromptStorage):
    _name: str
    _capacity: int
    _timeout: float
    _entries: list[tuple[ChatBranch, str, float]]
    _hit_chars: int
    _write_chars: int

    def __init__(self, name: str, capacity: int = 128, timeout: float = float('inf')):
        self._name = name
        self._capacity = capacity
        self._timeout = timeout
        self._entries = []
        self._hit_chars = 0
        self._write_chars = 0

    @property
    def name(self) -> str:
        return self._name

    def _expire(self, limit: int):
        now = time.time()
        expired = defaultdict(int)
        new_entries = []
        for p, m, t in self._entries:
            if now - t > self._timeout:
                expired[m] += p.cost
            else:
                new_entries.append((p, m, t))
        self._entries = new_entries
        while len(self._entries) > limit:
            p, m, _ = self._entries[0]
            expired[m] += p.cost
            self._entries.pop(0)
        for model, chars in expired.items():
            _logger.info(f"Prompt cache: -{chars / 1024:,.0} KB @ {self._name}/{model}")

    def _cached(self, prompt: ChatBranch, model: str) -> ChatBranch:
        best = ChatBranch()
        for cached_prompt, cached_model, _ in self._entries:
            if model != cached_model:
                continue
            prefix = prompt & cached_prompt
            if len(prefix) > len(best):
                best = prefix
        return best

    def cached(self, prompt: ChatBranch, model: str) -> ChatBranch:
        self._expire(self._capacity)
        return self._cached(prompt, model)

    def write(self, prompt: ChatBranch, model: str):
        hit = self._cached(prompt, model)
        self._expire(self._capacity - 1)
        self._entries.append((prompt, model, time.time()))
        self._hit_chars += hit.cost
        self._write_chars += prompt.cost
        _logger.info(f"Prompt cache: +{prompt.pretty_cost} ({hit.cost / prompt.cost:.0%} hit, {self._hit_chars / self._write_chars:.0%} overall) @ {self._name}/{model}")

    def purge(self):
        self._expire(0)

@cache
def create(name: str, capacity: int = 128, timeout: float = float('inf')) -> PromptStorage:
    return _LruPromptStorage(name, capacity, timeout)

__all__ = [
    'create',
]

