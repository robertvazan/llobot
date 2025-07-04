from __future__ import annotations
from anthropic import Anthropic
from llobot.chats import ChatRole, ChatBranch
from llobot.models import Model
from llobot.models.streams import ModelStream
from llobot.models.stats import ModelStats
from llobot.models.caches import PromptCache, PromptStorage
from llobot.models.estimators import TokenLengthEstimator
import llobot.models.caches
import llobot.models.caches.lru
import llobot.models.streams
import llobot.models.estimators

class _AnthropicStream(ModelStream):
    _length: int
    _stats: ModelStats
    _iterator: Iterator[str]

    def __init__(self,
        client: Anthropic,
        model: str,
        max_tokens: int,
        prompt: ChatBranch,
        cached: bool,
        temperature: float | None,
        top_k: int | None,
        top_p: float | None,
    ):
        super().__init__()
        self._length = prompt.cost
        self._stats = ModelStats()
        self._iterator = iter(self._iterate(client, model, max_tokens, prompt, cached, temperature, top_k, top_p))

    def _iterate(self,
        client: Anthropic,
        model: str,
        max_tokens: int,
        prompt: ChatBranch,
        cached: bool,
        temperature: float | None,
        top_k: int | None,
        top_p: float | None,
    ) -> Iterable[str]:
        messages = []
        for message in prompt:
            messages.append({
                'role': 'user' if message.role == ChatRole.USER else 'assistant',
                'content': message.content,
            })
        cacheable = prompt.context_only()
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
        if temperature is not None:
            parameters['temperature'] = temperature
        if top_k is not None:
            parameters['top_k'] = top_k
        if top_p is not None:
            parameters['top_p'] = top_p
        with client.messages.stream(**parameters) as stream:
            for chunk in stream.text_stream:
                self._length += len(chunk)
                yield chunk
            usage = stream.get_final_message().usage
            self._stats = ModelStats(
                # Annoyingly, Claude API does not include cache writes and reads in the total number of input tokens, so we sum it here.
                prompt_tokens = usage.input_tokens + (usage.cache_creation_input_tokens or 0) + (usage.cache_read_input_tokens or 0),
                response_tokens = usage.output_tokens,
                # If caching is enabled and there were no cache reads, we want to record zero to indicate cache miss.
                cached_tokens = (usage.cache_read_input_tokens or 0) if cached else usage.cache_read_input_tokens,
                total_chars = self._length,
            )

    def _receive(self) -> str | ModelStats:
        try:
            return next(self._iterator)
        except StopIteration:
            return self._stats

    def _close(self):
        self._iterator.close()

class _AnthropicModel(Model):
    _client: Anthropic
    _name: str
    _aliases: list[str]
    _context_budget: int
    _max_tokens: int
    _estimator: TokenLengthEstimator
    _cached: bool
    _cache: PromptStorage
    _temperature: float | None
    _top_k: int | None
    _top_p: float | None

    def __init__(self, name: str, *,
        client: Anthropic | None = None,
        auth: str | None = None,
        aliases: Iterable[str] = [],
        context_budget: int = 25_000,
        max_tokens: int = 8_000,
        estimator: TokenLengthEstimator = llobot.models.estimators.standard(),
        cached: bool = True,
        temperature: float | None = None,
        top_k: int | None = None,
        top_p: float | None = None,
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
        self._estimator = estimator
        self._cached = cached
        self._cache = llobot.models.caches.lru.create('anthropic', timeout=5*60) if cached else llobot.models.caches.disabled()
        self._temperature = temperature
        self._top_k = top_k
        self._top_p = top_p

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
        if self._temperature is not None:
            options['temperature'] = self._temperature
        if self._top_k is not None:
            options['top_k'] = self._top_k
        if self._top_p is not None:
            options['top_p'] = self._top_p
        return options

    def validate_options(self, options: dict):
        allowed = {'context_budget', 'max_tokens', 'temperature', 'top_k', 'top_p'}
        for unrecognized in set(options) - allowed:
            raise ValueError(f"Unrecognized option: {unrecognized}")

    def configure(self, options: dict) -> Model:
        temperature = options.get('temperature', self._temperature)
        top_k = options.get('top_k', self._top_k)
        top_p = options.get('top_p', self._top_p)
        return _AnthropicModel(
            self._name,
            client=self._client,
            context_budget=int(options.get('context_budget', self._context_budget)),
            max_tokens=int(options.get('max_tokens', self._max_tokens)),
            estimator=self._estimator,
            cached=self._cached,
            temperature=float(temperature) if temperature is not None and temperature != '' else None,
            top_k=int(top_k) if top_k else None,
            top_p=float(top_p) if top_p else None,
        )

    @property
    def context_budget(self) -> int:
        return self._context_budget

    @property
    def estimator(self) -> TokenLengthEstimator:
        return self._estimator

    @property
    def cache(self) -> PromptCache:
        return self._cache[self._name]

    def _connect(self, prompt: ChatBranch) -> ModelStream:
        result = _AnthropicStream(
            self._client,
            self._name,
            self._max_tokens,
            prompt,
            self._cached,
            self._temperature,
            self._top_k,
            self._top_p
        )
        result |= llobot.models.streams.notify(lambda _: self.cache.write(prompt.context_only()))
        return result

def create(name: str, **kwargs) -> Model:
    return _AnthropicModel(name, **kwargs)

__all__ = [
    'create',
]

