from __future__ import annotations
from google import genai
from google.genai import types
from llobot.chats import ChatRole, ChatBranch
from llobot.models import Model
from llobot.models.streams import ModelStream
from llobot.models.stats import ModelStats
from llobot.models.caches import PromptCache, PromptStorage
from llobot.models.estimators import TokenLengthEstimator
import llobot.models.openai
import llobot.models.estimators
import llobot.models.caches
import llobot.models.caches.lru
import llobot.models.streams

class _GeminiStream(ModelStream):
    _length: int
    _stats: ModelStats
    _iterator: Iterator[str]

    def __init__(self,
        client: genai.Client,
        model: str,
        prompt: ChatBranch,
        thinking: int | None = None,
        temperature: float | None = None,
    ):
        super().__init__()
        self._length = prompt.cost
        self._stats = ModelStats()
        self._iterator = iter(self._iterate(client, model, prompt, thinking, temperature))

    def _iterate(self,
        client: genai.Client,
        model: str,
        prompt: ChatBranch,
        thinking: int | None = None,
        temperature: float | None = None,
    ) -> Iterable[str]:
        contents = []
        for message in prompt:
            if message.role == ChatRole.USER:
                contents.append(types.UserContent(parts=[types.Part(text=message.content)]))
            else:
                contents.append(types.ModelContent(parts=[types.Part(text=message.content)]))
        config = types.GenerateContentConfig()
        if thinking is not None:
            config.thinking_config = types.ThinkingConfig(thinking_budget=thinking)
        if temperature is not None:
            config.temperature = temperature
        stream = client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=config,
        )
        last_chunk = None
        for chunk in stream:
            if chunk.text:
                self._length += len(chunk.text)
                yield chunk.text
            last_chunk = chunk
        if last_chunk:
            usage = last_chunk.usage_metadata
            self._stats = ModelStats(
                prompt_tokens = usage.prompt_token_count,
                response_tokens = usage.candidates_token_count,
                # Implicit caching is always enabled, so signal cache miss by reporting zero cached tokens if there were no cache reads.
                cached_tokens = usage.cached_content_token_count or 0,
                # Report zero thinking tokens when thinking is enabled and no thinking was done by the model.
                thinking_tokens = usage.thoughts_token_count or 0 if thinking is None or thinking > 0 else usage.thoughts_token_count,
                total_chars = self._length,
            )

    def _receive(self) -> str | ModelStats:
        try:
            return next(self._iterator)
        except StopIteration:
            return self._stats

class _GeminiModel(Model):
    _client: genai.Client
    _name: str
    _aliases: list[str]
    _context_budget: int
    _thinking: int | None
    _temperature: float | None
    _estimator: TokenLengthEstimator
    _cache: PromptStorage

    def __init__(self, name: str, *,
        client: genai.Client | None = None,
        auth: str | None = None,
        aliases: Iterable[str] = [],
        context_budget: int = 25_000,
        thinking: int | None = None,
        temperature: float | None = None,
        estimator: TokenLengthEstimator = llobot.models.estimators.standard(),
        cache: PromptStorage = llobot.models.caches.lru.create('gemini', timeout=5*60),
    ):
        if client:
            self._client = client
        elif auth:
            self._client = genai.Client(api_key=auth)
        else:
            # API key is taken from GOOGLE_API_KEY environment variable.
            self._client = genai.Client()
        self._name = name
        self._aliases = list(aliases)
        self._context_budget = context_budget
        self._thinking = thinking
        self._temperature = temperature
        self._estimator = estimator
        self._cache = cache

    @property
    def name(self) -> str:
        return f'gemini/{self._name}'

    @property
    def aliases(self) -> Iterable[str]:
        yield self._name
        yield from self._aliases

    @property
    def options(self) -> dict:
        options = {
            'context_budget': self._context_budget,
        }
        if self._thinking is not None:
            options['thinking'] = self._thinking
        if self._temperature is not None:
            options['temperature'] = self._temperature
        return options

    def validate_options(self, options: dict):
        allowed = {'context_budget', 'thinking', 'temperature'}
        for unrecognized in set(options) - allowed:
            raise ValueError(f"Unrecognized option: {unrecognized}")
        if options.get('temperature'):
            temperature = float(options['temperature'])
            if not (0.0 <= temperature <= 2.0):
                raise ValueError(f"Temperature must be between 0.0 and 2.0, got {temperature}")

    def configure(self, options: dict) -> Model:
        thinking = options.get('thinking', self._thinking)
        temperature = options.get('temperature', self._temperature)
        return _GeminiModel(
            self._name,
            client=self._client,
            aliases=self._aliases,
            context_budget=int(options.get('context_budget', self._context_budget)),
            thinking=int(thinking) if thinking else None,
            temperature=float(temperature) if temperature is not None and temperature != '' else None,
            estimator=self._estimator,
            cache=self._cache,
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
        self.cache.trim(prompt)
        result = _GeminiStream(
            self._client,
            self._name,
            prompt,
            self._thinking,
            self._temperature,
        )
        result |= llobot.models.streams.notify(lambda stream: self.cache.write(llobot.models.streams.chat(prompt, stream)))
        return result

def create(name: str, **kwargs) -> Model:
    return _GeminiModel(name, **kwargs)

def via_openai_protocol(name: str, auth: str, **kwargs) -> Model:
    return llobot.models.openai.compatible('https://generativelanguage.googleapis.com/v1beta/openai', 'gemini', name, auth=auth, **kwargs)

__all__ = [
    'create',
    'via_openai_protocol',
]

