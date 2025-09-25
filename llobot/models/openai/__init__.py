from __future__ import annotations
from typing import Iterable
import requests
from llobot.chats.branches import ChatBranch
from llobot.chats.intents import ChatIntent
from llobot.models import Model
from llobot.models.streams import ModelStream, buffer_stream
from llobot.chats.binarization import binarize_chat
from llobot.models.openai.endpoints import proprietary_openai_endpoint
from llobot.models.openai.encoding import encode_request, parse_stream
from llobot.utils.values import ValueTypeMixin

class OpenAIModel(Model, ValueTypeMixin):
    """
    A model that uses an OpenAI or OpenAI-compatible API.
    """
    _name: str
    _model: str
    _endpoint: str
    _auth: str
    _context_budget: int

    def __init__(self, name: str, *,
        model: str = 'gpt-5',
        auth: str = '',
        endpoint: str | None = None,
        context_budget: int = 100_000,
    ):
        """
        Initializes the OpenAI model.

        Args:
            name: The name for this model instance in llobot.
            model: The model ID to use with the API. Defaults to 'gpt-5'.
            auth: The API key. For OpenAI, this is required. For other providers,
                  it may be optional.
            endpoint: The base URL of the API endpoint. Defaults to the
                      official OpenAI API endpoint.
            context_budget: The character budget for context stuffing.
        """
        self._name = name
        self._model = model
        self._endpoint = endpoint or proprietary_openai_endpoint()
        self._auth = auth
        self._context_budget = context_budget

    def _ephemeral_fields(self) -> Iterable[str]:
        return ['_auth']

    @property
    def name(self) -> str:
        return self._name

    @property
    def context_budget(self) -> int:
        return self._context_budget

    def generate(self, prompt: ChatBranch) -> ModelStream:
        def _stream() -> ModelStream:
            sanitized_prompt = binarize_chat(prompt, last=ChatIntent.PROMPT)
            request = encode_request(self._model, sanitized_prompt)
            headers = {}
            if self._auth:
                headers['Authorization'] = f'Bearer {self._auth}'
            with requests.post(self._endpoint + '/chat/completions', stream=True, json=request, headers=headers) as http_response:
                http_response.raise_for_status()
                if http_response.encoding is None:
                    http_response.encoding = 'utf-8'
                yield ChatIntent.RESPONSE
                yield from parse_stream(http_response.iter_lines(decode_unicode=True))
        return buffer_stream(_stream())

__all__ = [
    'OpenAIModel',
]
