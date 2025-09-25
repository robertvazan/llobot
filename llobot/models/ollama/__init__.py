from __future__ import annotations
from typing import Iterable
import requests
from llobot.chats.branches import ChatBranch
from llobot.chats.intents import ChatIntent
from llobot.models import Model
from llobot.models.streams import ModelStream, buffer_stream
from llobot.chats.binarization import binarize_chat
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
    _context_budget: int

    def __init__(self, name: str, *,
        model: str,
        num_ctx: int,
        endpoint: str | None = None,
        context_budget: int | None = None,
    ):
        """
        Initializes the Ollama model.

        Context size (`num_ctx`) is a mandatory parameter, because Ollama has
        only a 2K-token default, which is useless for real applications.

        Args:
            name: The name for this model instance in llobot.
            model: The model ID to use with Ollama (e.g., 'qwen2:7b').
            num_ctx: The context window size for the model.
            endpoint: The URL of the Ollama API endpoint. Defaults to localhost.
            context_budget: The character budget for context stuffing. Defaults
                            to `2 * num_ctx`, with a cap of 100,000.
        """
        self._name = name
        self._model = model
        self._endpoint = endpoint or localhost_ollama_endpoint()
        self._num_ctx = num_ctx
        # Default context budget to half the num_ctx, assuming about 4 characters per token.
        self._context_budget = context_budget or min(100_000, 2 * num_ctx)

    @property
    def name(self) -> str:
        return self._name

    @property
    def context_budget(self) -> int:
        return self._context_budget

    def generate(self, prompt: ChatBranch) -> ModelStream:
        def _stream() -> ModelStream:
            sanitized_prompt = binarize_chat(prompt, last=ChatIntent.PROMPT)
            request = encode_request(self._model, {'num_ctx': self._num_ctx}, sanitized_prompt)
            with requests.post(self._endpoint + '/chat', stream=True, json=request) as http_response:
                http_response.raise_for_status()
                yield ChatIntent.RESPONSE
                yield from parse_stream(http_response.iter_lines())
        return buffer_stream(_stream())

__all__ = [
    'OllamaModel',
]
