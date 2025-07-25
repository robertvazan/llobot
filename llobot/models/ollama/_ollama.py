from __future__ import annotations
from functools import cache
import json
import requests
from llobot.chats import ChatBranch
from llobot.models import Model
from llobot.models.streams import ModelStream
import llobot.models.streams

class _OllamaStream(ModelStream):
    def __init__(self, endpoint: str, model: str, options: dict, prompt: ChatBranch):
        super().__init__()
        from llobot.models.ollama import encoding
        request = encoding.encode_request(model, options, prompt)
        self._http_response = requests.post(endpoint + '/chat', stream=True, json=request)
        self._http_response.raise_for_status()
        self._iterator = encoding.parse_stream(self._http_response.iter_lines())

    def _receive(self) -> str | None:
        return next(self._iterator, None)

    def _close(self):
        self._http_response.close()

class _OllamaModel(Model):
    # Normalized Ollama name: no ollama/ prefix and no :latest suffix.
    _name: str
    _aliases: list[str]
    _endpoint: str
    _num_ctx: int
    _context_budget: int

    # Context size is a mandatory parameter, because Ollama has only 2K-token default, which is useless for real applications.
    def __init__(self, name: str, num_ctx: int, *,
        endpoint: str | None = None,
        aliases: Iterable[str] = [],
        context_budget: int | None = None,
    ):
        from llobot.models.ollama import endpoints
        self._name = name.removeprefix('ollama/').removesuffix(':latest')
        self._aliases = list(aliases)
        self._endpoint = endpoint or endpoints.localhost()
        self._num_ctx = num_ctx
        # Default context budget to half the num_ctx, assuming about 4 characters per token.
        self._context_budget = context_budget or min(100_000, 2 * num_ctx)

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
        options = {
            'num_ctx': self._num_ctx,
            'context_budget': self._context_budget,
        }
        return options

    def validate_options(self, options: dict):
        allowed = {'num_ctx', 'context_budget'}
        for unrecognized in set(options) - allowed:
            raise ValueError(f"Unrecognized option: {unrecognized}")

    def configure(self, options: dict) -> Model:
        return _OllamaModel(
            self._name,
            int(options.get('num_ctx', self._num_ctx)),
            endpoint=self._endpoint,
            aliases=self._aliases,
            context_budget=int(options.get('context_budget', self._context_budget)),
        )

    @property
    def context_budget(self) -> int:
        return self._context_budget

    def generate(self, prompt: ChatBranch) -> ModelStream:
        options = self.options
        del options['context_budget']
        return _OllamaStream(self._endpoint, self._name, options, prompt)

# Default tag is :latest.
def create(name: str, num_ctx: int, **kwargs) -> Model:
    return _OllamaModel(name, num_ctx, **kwargs)

__all__ = [
    'create',
]

