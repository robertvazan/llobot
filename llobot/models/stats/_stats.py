from __future__ import annotations
from collections.abc import Mapping

class ModelStats(Mapping):
    _data: dict[str, Any]

    def __init__(self, data: dict[str, Any] = {}, **kwargs):
        self._data = {key.replace('_', '-'): value for key, value in (data | kwargs).items() if value is not None}

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    # Prompt token count covers the whole submitted prompt
    # regardless of how much of the prompt was processed or just retrieved from cache.
    # Prompt tokens would ideally exclude the invisible system prompt inserted by the cloud,
    # but we usually have no way to subtract it from the total prompt tokens, so it's counted in.
    @property
    def prompt_tokens(self) -> int | None:
        return self._data.get('prompt-tokens', None)

    # Repsonse tokens cover only the visible part of the prompt.
    # Since thinking is usually hidden in current models, it is not included here.
    @property
    def response_tokens(self) -> int | None:
        return self._data.get('response-tokens', None)

    # This covers all visible tokens in prompt and response.
    # All prompt tokens are included in the total, whether they are cached or not.
    # Since thinking tokens are hidden in most current models, they are not counted into the total.
    @property
    def total_tokens(self) -> int | None:
        if 'total-tokens' in self._data:
            return self._data['total-tokens']
        if self.prompt_tokens is not None and self.response_tokens is not None:
            return self.prompt_tokens + self.response_tokens
        return None

    # Part of the prompt that was successfully retrieved from the cache.
    # This may be zero if caching is enabled but it was a cache miss.
    @property
    def cached_tokens(self) -> int | None:
        return self._data.get('cached-tokens', None)

    # Number of thinking tokens that were spent before the response was generated.
    @property
    def thinking_tokens(self) -> int | None:
        return self._data.get('thinking-tokens', None)

    @property
    def total_chars(self) -> int | None:
        return self._data.get('total-chars', None)

    @property
    def token_length(self) -> float | None:
        if 'token-length' in self._data:
            return self._data['token-length']
        if self.total_chars and self.total_tokens:
            return self.total_chars / self.total_tokens
        return None

    @property
    def load_seconds(self) -> float | None:
        return self._data.get('load-seconds', None)

    @property
    def prompt_seconds(self) -> float | None:
        return self._data.get('prompt-seconds', None)

    @property
    def response_seconds(self) -> float | None:
        return self._data.get('response-seconds', None)

    @property
    def total_seconds(self) -> float | None:
        if 'token-seconds' in self._data:
            return self._data['token-seconds']
        if self.load_seconds is not None and self.prompt_seconds is not None and self.response_seconds is not None:
            return self.load_seconds + self.prompt_seconds + self.response_seconds
        return None

    def __str__(self) -> str:
        return str(dict(self))

    def __or__(self, other: ModelStats) -> ModelStats:
        return ModelStats(self._data | other._data)

    def __add__(self, other: ModelStats) -> ModelStats:
        data = {}
        for key in set(self._data.keys()) | set(other._data.keys()):
            value1 = self._data.get(key)
            value2 = other._data.get(key)
            if isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
                data[key] = value1 + value2
            else:
                data[key] = value1 if value2 is None else value2
        return ModelStats(data)

__all__ = [
    'ModelStats',
]

