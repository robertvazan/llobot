from __future__ import annotations
from typing import Iterable
from anthropic import Anthropic
from llobot.chats.intent import ChatIntent
from llobot.chats.thread import ChatThread
from llobot.models import Model
from llobot.chats.stream import ChatStream, buffer_stream
from llobot.formats.binarization import BinarizationFormat, standard_binarization_format
from llobot.utils.values import ValueTypeMixin

class AnthropicModel(Model, ValueTypeMixin):
    """
    A model that uses the Anthropic API (e.g., Claude).
    """
    _name: str
    _model: str
    _client: Anthropic
    _max_tokens: int
    _cached: bool
    _thinking: int | None
    _binarization_format: BinarizationFormat

    def __init__(self, *,
        model: str,
        name: str | None = None,
        client: Anthropic | None = None,
        auth: str | None = None,
        max_tokens: int = 8_000,
        # No caching by default. It costs extra and not everyone takes advantage of it.
        cached: bool = False,
        thinking: int | None = None,
        binarization_format: BinarizationFormat | None = None,
    ):
        """
        Initializes the Anthropic model.

        Args:
            model: The actual model ID to use with the Anthropic API. Mandatory.
            name: The name for this model instance in llobot. Defaults to model ID.
            client: An existing `Anthropic` client instance. If not provided, a new one is created.
            auth: Your Anthropic API key. If not provided, the `ANTHROPIC_API_KEY` environment
                  variable is used.
            max_tokens: The maximum number of tokens to generate.
            cached: Whether to use Anthropic's caching feature.
            thinking: The budget in tokens to allocate for "thinking" (prompt construction).
            binarization_format: Format to use for prompt binarization. Defaults to standard.
        """
        self._name = name if name is not None else model
        self._model = model
        if client:
            self._client = client
        elif auth:
            self._client = Anthropic(api_key=auth)
        else:
            # API key is taken from ANTHROPIC_API_KEY environment variable.
            self._client = Anthropic()
        self._max_tokens = max_tokens
        self._cached = cached
        self._thinking = thinking
        self._binarization_format = binarization_format or standard_binarization_format()

    def _ephemeral_fields(self) -> Iterable[str]:
        return ['_client']

    @property
    def name(self) -> str:
        return self._name

    @property
    def identifier(self) -> str:
        return f'anthropic/{self._model}'

    def generate(self, prompt: ChatThread) -> ChatStream:
        def _stream() -> ChatStream:
            messages = []
            sanitized_prompt = self._binarization_format.binarize_chat(prompt)
            for message in sanitized_prompt:
                messages.append({
                    'role': 'user' if message.intent == ChatIntent.PROMPT else 'assistant',
                    'content': message.content,
                })
            parameters = {
                'model': self._model,
                'max_tokens': self._max_tokens,
                'messages': messages,
            }
            if self._cached:
                parameters['cache_control'] = {'type': 'ephemeral'}
            if self._thinking is not None:
                parameters['thinking'] = {
                    "type": "enabled",
                    "budget_tokens": self._thinking
                }
            yield ChatIntent.RESPONSE
            with self._client.messages.stream(**parameters) as stream:
                yield from stream.text_stream
        return buffer_stream(_stream())

__all__ = [
    'AnthropicModel',
]
