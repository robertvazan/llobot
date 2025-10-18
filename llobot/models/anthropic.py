from __future__ import annotations
from typing import Iterable
from anthropic import Anthropic
from llobot.chats.intent import ChatIntent
from llobot.chats.thread import ChatThread
from llobot.models import Model
from llobot.chats.stream import ChatStream, buffer_stream
from llobot.chats.binarization import binarize_chat
from llobot.utils.values import ValueTypeMixin

class AnthropicModel(Model, ValueTypeMixin):
    """
    A model that uses the Anthropic API (e.g., Claude).
    """
    _name: str
    _model: str
    _client: Anthropic
    _context_budget: int
    _max_tokens: int
    _cached: bool
    _thinking: int | None

    def __init__(self, name: str, *,
        model: str = 'claude-sonnet-4-0',
        client: Anthropic | None = None,
        auth: str | None = None,
        context_budget: int = 100_000,
        max_tokens: int = 8_000,
        # No caching by default. It costs extra and not everyone takes advantage of it.
        cached: bool = False,
        thinking: int | None = None,
    ):
        """
        Initializes the Anthropic model.

        Args:
            name: The name for this model instance in llobot.
            model: The actual model ID to use with the Anthropic API. Defaults to 'claude-sonnet-4-0'.
            client: An existing `Anthropic` client instance. If not provided, a new one is created.
            auth: Your Anthropic API key. If not provided, the `ANTHROPIC_API_KEY` environment
                  variable is used.
            context_budget: The character budget for context stuffing.
            max_tokens: The maximum number of tokens to generate.
            cached: Whether to use Anthropic's caching feature.
            thinking: The budget in tokens to allocate for "thinking" (prompt construction).
        """
        self._name = name
        self._model = model
        if client:
            self._client = client
        elif auth:
            self._client = Anthropic(api_key=auth)
        else:
            # API key is taken from ANTHROPIC_API_KEY environment variable.
            self._client = Anthropic()
        self._context_budget = context_budget
        self._max_tokens = max_tokens
        self._cached = cached
        self._thinking = thinking

    def _ephemeral_fields(self) -> Iterable[str]:
        return ['_client']

    @property
    def name(self) -> str:
        return self._name

    @property
    def context_budget(self) -> int:
        return self._context_budget

    def generate(self, prompt: ChatThread) -> ChatStream:
        def _stream() -> ChatStream:
            messages = []
            sanitized_prompt = binarize_chat(prompt, last=ChatIntent.PROMPT)
            for message in sanitized_prompt:
                messages.append({
                    'role': 'user' if message.intent == ChatIntent.PROMPT else 'assistant',
                    'content': message.content,
                })
            # Skip the last message, which is the user's prompt, because it tends to be frequently edited.
            cacheable = sanitized_prompt[:-1]
            if self._cached and cacheable:
                breakpoints = [int(bp * cacheable.cost) for bp in (0.25, 0.5, 0.75, 1.0)]
                cumulative = 0
                for i, message in enumerate(cacheable):
                    cumulative += message.cost
                    if breakpoints and cumulative >= breakpoints[0]:
                        messages[i]['content'] = [{'type': 'text', 'text': messages[i]['content'], 'cache_control': {'type': 'ephemeral'}}]
                        breakpoints.pop(0)
            parameters = {
                'model': self._model,
                'max_tokens': self._max_tokens,
                'messages': messages,
            }
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
