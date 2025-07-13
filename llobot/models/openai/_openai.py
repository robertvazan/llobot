from __future__ import annotations
from functools import cache
import requests
from llobot.chats import ChatBranch
from llobot.models import Model
from llobot.models.streams import ModelStream
import llobot.models.streams

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

    def _receive(self) -> str | None:
        return next(self._iterator, None)

    def _close(self):
        self._http_response.close()

class _OpenAIModel(Model):
    _namespace: str
    _name: str
    _aliases: list[str]
    _endpoint: str
    _auth: str
    _context_budget: int
    _temperature: float | None

    def __init__(self, name: str, *,
        auth: str = '',
        endpoint: str | None = None,
        namespace: str = 'openai',
        aliases: list[str] = [],
        context_budget: int = 100_000,
        temperature: float | None = None,
    ):
        from llobot.models.openai import endpoints
        self._namespace = namespace
        self._name = name
        self._aliases = aliases
        self._endpoint = endpoint or endpoints.proprietary()
        self._auth = auth
        self._context_budget = context_budget
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
        options = { 'context_budget': self._context_budget }
        if self._temperature is not None:
            options['temperature'] = self._temperature
        return options

    def validate_options(self, options: dict):
        allowed = {'context_budget', 'temperature'}
        for unrecognized in set(options) - allowed:
            raise ValueError(f"Unrecognized option: {unrecognized}")

    def configure(self, options: dict) -> Model:
        temperature = options.get('temperature', self._temperature)
        return _OpenAIModel(self._name,
            auth=self._auth,
            endpoint=self._endpoint,
            namespace=self._namespace,
            aliases=self._aliases,
            context_budget=int(options.get('context_budget', self._context_budget)),
            temperature=float(temperature) if temperature is not None and temperature != '' else None,
        )

    @property
    def context_budget(self) -> int:
        return self._context_budget

    def generate(self, prompt: ChatBranch) -> ModelStream:
        return _OpenAIStream(self._endpoint, self._auth, self._name, self.options, prompt)

def proprietary(name: str, auth: str, **kwargs) -> Model:
    return _OpenAIModel(name, auth=auth, **kwargs)

def compatible(endpoint: str, namespace: str, name: str, **kwargs) -> Model:
    return _OpenAIModel(name, endpoint=endpoint, namespace=namespace, **kwargs)

__all__ = [
    'proprietary',
    'compatible',
]

