from __future__ import annotations
from typing import Iterable
import requests
from llobot.chats.thread import ChatThread
from llobot.chats.intent import ChatIntent
from llobot.models import Model
from llobot.chats.stream import ChatStream, buffer_stream
from llobot.formats.binarization import BinarizationFormat, standard_binarization_format
from llobot.models.ollama.endpoints import localhost_ollama_endpoint
from llobot.models.ollama.encoding import encode_request, parse_stream
from llobot.utils.values import ValueTypeMixin

class OllamaModel(Model, ValueTypeMixin):
    """
    A model that uses a local or remote Ollama instance.
    """
    _name: str
    _model: str
    _endpoint: str
    _num_ctx: int
    _binarization_format: BinarizationFormat

    def __init__(self, *,
        model: str,
        num_ctx: int,
        name: str | None = None,
        endpoint: str | None = None,
        binarization_format: BinarizationFormat | None = None,
    ):
        """
        Initializes the Ollama model.

        Context size (`num_ctx`) is a mandatory parameter, because Ollama has
        only a 2K-token default, which is useless for real applications.

        Args:
            model: The model ID to use with Ollama (e.g., 'qwen2:7b').
            num_ctx: The context window size for the model.
            name: The name for this model instance in llobot. Defaults to model ID.
            endpoint: The URL of the Ollama API endpoint. Defaults to localhost.
            binarization_format: Format to use for prompt binarization. Defaults to standard.
        """
        self._name = name if name is not None else model
        self._model = model
        self._endpoint = endpoint or localhost_ollama_endpoint()
        self._num_ctx = num_ctx
        self._binarization_format = binarization_format or standard_binarization_format()

    @property
    def name(self) -> str:
        return self._name

    @property
    def identifier(self) -> str:
        return f'ollama/{self._model}'

    def generate(self, prompt: ChatThread) -> ChatStream:
        def _stream() -> ChatStream:
            sanitized_prompt = self._binarization_format.binarize_chat(prompt)
            request = encode_request(self._model, {'num_ctx': self._num_ctx}, sanitized_prompt)
            yield ChatIntent.RESPONSE
            with requests.post(self._endpoint + '/chat', stream=True, json=request) as http_response:
                http_response.raise_for_status()
                yield from parse_stream(http_response.iter_lines())
        return buffer_stream(_stream())

__all__ = [
    'OllamaModel',
]
