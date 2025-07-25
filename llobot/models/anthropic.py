from __future__ import annotations
from anthropic import Anthropic
from llobot.chats import ChatRole, ChatBranch
from llobot.models import Model
from llobot.models.streams import ModelStream
import llobot.models.streams

class _AnthropicStream(ModelStream):
    _iterator: Iterator[str]

    def __init__(self,
        client: Anthropic,
        model: str,
        max_tokens: int,
        prompt: ChatBranch,
        cached: bool,
        thinking: int | None,
    ):
        super().__init__()
        self._iterator = self._iterate(client, model, max_tokens, prompt, cached, thinking)

    def _iterate(self,
        client: Anthropic,
        model: str,
        max_tokens: int,
        prompt: ChatBranch,
        cached: bool,
        thinking: int | None,
    ) -> Iterable[str]:
        messages = []
        for message in prompt:
            messages.append({
                'role': 'user' if message.role == ChatRole.USER else 'assistant',
                'content': message.content,
            })
        # Skip the last message, which is the user's prompt, because it tends to be frequently edited.
        cacheable = prompt[:-1]
        if cached and cacheable:
            breakpoints = [int(bp * cacheable.cost) for bp in (0.25, 0.5, 0.75, 1.0)]
            cumulative = 0
            for i, message in enumerate(cacheable):
                cumulative += message.cost
                if breakpoints and cumulative >= breakpoints[0]:
                    messages[i]['content'] = [{'type': 'text', 'text': messages[i]['content'], 'cache_control': {'type': 'ephemeral'}}]
                    breakpoints.pop(0)
        parameters = {
            'model': model,
            'max_tokens': max_tokens,
            'messages': messages,
        }
        if thinking is not None:
            parameters['thinking'] = {
                "type": "enabled",
                "budget_tokens": thinking
            }
        with client.messages.stream(**parameters) as stream:
            for chunk in stream.text_stream:
                yield chunk

    def _receive(self) -> str | None:
        try:
            return next(self._iterator)
        except StopIteration:
            return None

    def _close(self):
        self._iterator.close()

class _AnthropicModel(Model):
    _client: Anthropic
    _name: str
    _aliases: list[str]
    _context_budget: int
    _max_tokens: int
    _cached: bool
    _thinking: int | None

    def __init__(self, name: str, *,
        client: Anthropic | None = None,
        auth: str | None = None,
        aliases: Iterable[str] = [],
        context_budget: int = 100_000,
        max_tokens: int = 8_000,
        # No caching by default. It costs extra and not everyone takes advantage of it.
        cached: bool = False,
        thinking: int | None = None,
    ):
        if client:
            self._client = client
        elif auth:
            self._client = Anthropic(api_key=auth)
        else:
            # API key is taken from ANTHROPIC_API_KEY environment variable.
            self._client = Anthropic()
        self._name = name
        self._aliases = list(aliases)
        self._context_budget = context_budget
        self._max_tokens = max_tokens
        self._cached = cached
        self._thinking = thinking

    @property
    def name(self) -> str:
        return f'anthropic/{self._name}'

    @property
    def aliases(self) -> Iterable[str]:
        yield self._name
        yield from self._aliases

    @property
    def options(self) -> dict:
        options = {
            'context_budget': self._context_budget,
            'max_tokens': self._max_tokens,
        }
        if self._thinking is not None:
            options['thinking'] = self._thinking
        return options

    def validate_options(self, options: dict):
        allowed = {'context_budget', 'max_tokens', 'thinking'}
        for unrecognized in set(options) - allowed:
            raise ValueError(f"Unrecognized option: {unrecognized}")

    def configure(self, options: dict) -> Model:
        thinking_opt = options.get('thinking', self._thinking)
        return _AnthropicModel(
            self._name,
            client=self._client,
            context_budget=int(options.get('context_budget', self._context_budget)),
            max_tokens=int(options.get('max_tokens', self._max_tokens)),
            cached=self._cached,
            thinking=int(thinking_opt) if thinking_opt is not None else None,
        )

    @property
    def context_budget(self) -> int:
        return self._context_budget

    def generate(self, prompt: ChatBranch) -> ModelStream:
        return _AnthropicStream(
            self._client,
            self._name,
            self._max_tokens,
            prompt,
            self._cached,
            self._thinking,
        )

def create(name: str, **kwargs) -> Model:
    return _AnthropicModel(name, **kwargs)

__all__ = [
    'create',
]

