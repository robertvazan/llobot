from __future__ import annotations
from functools import cache
import json
import requests
from llobot.chats import ChatBranch
from llobot.models import Model
from llobot.models.streams import ModelStream
from llobot.models.stats import ModelStats
from llobot.models.caches import PromptCache, PromptStorage
from llobot.models.estimators import TokenLengthEstimator
import llobot.models.streams
import llobot.models.estimators
import llobot.models.caches.last

class _OllamaStream(ModelStream):
    def __init__(self, endpoint: str, model: str, options: dict, prompt: ChatBranch):
        super().__init__()
        from llobot.models.ollama import encoding
        request = encoding.encode_request(model, options, prompt)
        self._http_response = requests.post(endpoint + '/chat', stream=True, json=request)
        self._http_response.raise_for_status()
        self._iterator = encoding.parse_stream(self._http_response.iter_lines())
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

class _OllamaModel(Model):
    # Normalized Ollama name: no ollama/ prefix and no :latest suffix.
    _name: str
    _aliases: list[str]
    _endpoint: str
    _context_size: int
    _estimator: TokenLengthEstimator
    _cache: PromptStorage
    _top_k: int | None

    # Context size is a mandatory parameter for two reasons. Firstly, Ollama has only 2K-token default, which is useless for real applications.
    # Secondly, even if Ollama introduces better default in the future, we don't have any easy way to query it.
    def __init__(self, name: str, context_size: int, *,
        endpoint: str | None = None,
        aliases: Iterable[str] = [],
        estimator: TokenLengthEstimator = llobot.models.estimators.standard(),
        cache: PromptStorage | None = None,
        top_k: int | None = None,
    ):
        from llobot.models.ollama import endpoints
        self._name = name.removeprefix('ollama/').removesuffix(':latest')
        self._aliases = list(aliases)
        self._endpoint = endpoint or endpoints.localhost()
        self._context_size = context_size
        self._estimator = estimator
        # Ollama does not have proper prompt cache in system RAM, only one or more inference buffers in VRAM,
        # so pessimistically assume there is only one prompt cache per endpoint.
        # Do not set any timeout, because any serious local Ollama setup is going to have cache that never expires.
        # This code assumes that create() below is a cached function.
        self._cache = cache or llobot.models.caches.last.create('ollama/' + endpoints.concise(self._endpoint))
        self._top_k = top_k

    @property
    def name(self) -> str:
        return f'ollama/{self._name}'

    @property
    def aliases(self) -> Iterable[str]:
        yield self._name
        if ':' in self._name:
            yield self._name.split(':')[0]
        yield from self._aliases

    @property
    def options(self) -> dict:
        options = { 'num_ctx': self._context_size }
        if self._top_k is not None:
            options['top_k'] = self._top_k
        return options

    def validate_options(self, options: dict):
        allowed = {'num_ctx', 'top_k'}
        for unrecognized in set(options) - allowed:
            raise ValueError(f"Unrecognized option: {unrecognized}")

    def configure(self, options: dict) -> Model:
        top_k = options.get('top_k', self._top_k)
        return _OllamaModel(
            self._name,
            int(options.get('num_ctx', self._context_size)),
            endpoint=self._endpoint,
            aliases=self._aliases,
            estimator=self._estimator,
            cache=self._cache,
            top_k=int(top_k) if top_k else None,
        )

    @property
    def context_size(self) -> int:
        return self._context_size

    @property
    def estimator(self) -> TokenLengthEstimator:
        return self._estimator

    @property
    def cache(self) -> PromptCache:
        # Not all options influence cache content, but Ollama so far does not care and restarts llama.cpp whenever any inference option changes.
        # There are always some options, at least context size. We will use short name, because Ollama server is going to host only Ollama models.
        return self._cache[self._name + '?' + '&'.join([f'{key}={value}' for key, value in sorted(self.options.items())])]

    def _connect(self, prompt: ChatBranch) -> ModelStream:
        self.cache.trim(prompt)
        result = _OllamaStream(self._endpoint, self._name, self.options, prompt)
        result |= llobot.models.streams.notify(lambda stream: self.cache.write(llobot.models.streams.chat(prompt, stream)))
        return result

# Default tag is :latest.
def create(name: str, context_size: int, **kwargs) -> Model:
    return _OllamaModel(name, context_size, **kwargs)

__all__ = [
    'create',
]

