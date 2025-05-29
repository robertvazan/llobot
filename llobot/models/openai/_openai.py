from __future__ import annotations
from functools import cache
import requests
from llobot.chats import ChatBranch
from llobot.models import Model
from llobot.models.streams import ModelStream
from llobot.models.stats import ModelStats
from llobot.models.caches import PromptCache, PromptStorage
from llobot.models.estimators import TokenLengthEstimator
import llobot.models.streams
import llobot.models.estimators
import llobot.models.caches
import llobot.models.caches.lru

class _OpenAIStream(ModelStream):
    def __init__(self, endpoint: str, auth: str, model: str, options: dict, prompt: ChatBranch):
        super().__init__()
        from llobot.models.openai import encoding
        request = encoding.encode_request(model, options, prompt)
        headers = {}
        if auth:
            headers['Authorization'] = f'Bearer {auth}'
        self._http_response = requests.post(endpoint + '/chat/completions', stream=True, json=request, headers=headers)
        self._http_response.raise_for_status()
        if self._http_response.encoding is None:
            self._http_response.encoding = 'utf-8'
        self._iterator = encoding.parse_stream(self._http_response.iter_lines(decode_unicode=True))
        self._length = prompt.cost

    def _receive(self) -> str | ModelStats:
        event = next(self._iterator, None)
        # Improperly terminated stream?
        if event is None:
            return ModelStats()
        if isinstance(event, ModelStats):
            return event | ModelStats(total_chars=self._length)
        self._length += len(event)
        return event

    def _close(self):
        self._http_response.close()

class _OpenAIModel(Model):
    _namespace: str
    _name: str
    _aliases: list[str]
    _endpoint: str
    _auth: str
    _context_size: int
    _estimator: TokenLengthEstimator
    _cache: PromptStorage
    _cache_sensitivity: set[str]
    _temperature: float | None

    # Context size is a mandatory, because we don't have any easy way to query it.
    # Not to mention OpenAI-provided context window is huge and we never want to use it fully.
    def __init__(self, name: str, context_size: int, *,
        auth: str = '',
        endpoint: str | None = None,
        namespace: str = 'openai',
        aliases: list[str] = [],
        estimator: TokenLengthEstimator = llobot.models.estimators.standard(),
        cache: PromptStorage = llobot.models.caches.disabled(),
        cache_sensitivity: set[str] = set(),
        temperature: float | None = None,
    ):
        from llobot.models.openai import endpoints
        self._namespace = namespace
        self._name = name
        self._aliases = aliases
        self._endpoint = endpoint or endpoints.proprietary()
        self._auth = auth
        self._context_size = context_size
        self._estimator = estimator
        # Proprietary OpenAI models have short-lived cache that could pessimistically exist only for 5 minutes.
        self._cache = cache
        self._cache_sensitivity = cache_sensitivity
        self._temperature = temperature

    @property
    def name(self) -> str:
        return f'{self._namespace}/{self._name}'

    @property
    def aliases(self) -> list[str]:
        yield self._name
        yield from self._aliases

    @property
    def options(self) -> dict:
        options = { 'context_size': self._context_size }
        if self._temperature is not None:
            options['temperature'] = self._temperature
        return options

    def validate_options(self, options: dict):
        allowed = {'context_size', 'temperature'}
        for unrecognized in set(options) - allowed:
            raise ValueError(f"Unrecognized option: {unrecognized}")

    def configure(self, options: dict) -> Model:
        temperature = options.get('temperature', self._temperature)
        return _OpenAIModel(self._name,
            int(options.get('context_size', self._context_size)),
            auth=self._auth,
            endpoint=self._endpoint,
            namespace=self._namespace,
            aliases=self._aliases,
            estimator=self._estimator,
            cache=self._cache,
            temperature=float(temperature) if temperature is not None and temperature != '' else None,
        )

    @property
    def context_size(self) -> int:
        return self._context_size

    @property
    def estimator(self):
        return self._estimator

    @property
    def cache(self) -> PromptCache:
        # By default, assume that options have no influence on cache validity, but allow overrides for compatible servers.
        # We are using the short name here, because cache storage is usually endpoint-local as are model names.
        sensitive_options = self._cache_sensitivity & self.options.keys()
        if sensitive_options:
            return self._cache[self._name + '?' + '&'.join([f'{key}={value}' for key, value in sorted(self.options.items()) if key in sensitive_options])]
        else:
            return self._cache[self._name]

    def _connect(self, prompt: ChatBranch) -> ModelStream:
        self.cache.trim(prompt)
        result = _OpenAIStream(self._endpoint, self._auth, self._name, self.options, prompt)
        result |= llobot.models.streams.notify(lambda stream: self.cache.write(llobot.models.streams.chat(prompt, stream)))
        return result

# Always specify context size. This must be a conscious cost-benefit decision.
def proprietary(name: str, context_size: int, auth: str, *, cache: PromptStorage = llobot.models.caches.lru.create('openai', timeout=5*60), **kwargs) -> Model:
    return _OpenAIModel(name, context_size, auth=auth, cache=cache, **kwargs)

def compatible(endpoint: str, namespace: str, name: str, context_size: int, **kwargs) -> Model:
    return _OpenAIModel(name, context_size, endpoint=endpoint, namespace=namespace, **kwargs)

__all__ = [
    'proprietary',
    'compatible',
]

