"""
Client for OpenAI models.
"""
from __future__ import annotations
from typing import Any, Iterable, cast
from openai import OpenAI, NOT_GIVEN
from openai.types.shared.reasoning_effort import ReasoningEffort
from llobot.formats.binarization import BinarizationFormat, standard_binarization_format
from llobot.chats.thread import ChatThread
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.models import Model
from llobot.chats.stream import ChatStream, buffer_stream
from llobot.utils.values import ValueTypeMixin

def _encode_role(intent: ChatIntent) -> str:
    if intent == ChatIntent.RESPONSE:
        return 'assistant'
    else:
        return 'user'

def _encode_message(message: ChatMessage) -> dict[str, str]:
    return {
        'role': _encode_role(message.intent),
        'content': message.content
    }

def _encode_chat(chat: ChatThread) -> list[dict[str, str]]:
    return [_encode_message(message) for message in chat]

class OpenAIModel(Model, ValueTypeMixin):
    """
    A model that uses the OpenAI API.
    """
    _name: str
    _model: str
    _auth: str | None
    _reasoning: ReasoningEffort | None
    _binarization_format: BinarizationFormat

    def __init__(self, *,
        model: str,
        auth: str | None = None,
        name: str | None = None,
        reasoning: ReasoningEffort | None = None,
        binarization_format: BinarizationFormat | None = None,
    ):
        """
        Initializes the OpenAI model.

        Args:
            model: The model ID to use with the API. Mandatory.
            auth: The API key for OpenAI. If None, uses OPENAI_API_KEY env var.
            name: The name for this model instance in llobot. Defaults to model ID.
            reasoning: Reasoning effort for the model. Defaults to None (use API default).
            binarization_format: Format to use for prompt binarization. Defaults to standard.
        """
        self._name = name if name is not None else model
        self._model = model
        self._auth = auth
        self._reasoning = reasoning
        self._binarization_format = binarization_format or standard_binarization_format()

    def _ephemeral_fields(self) -> Iterable[str]:
        return ['_auth']

    @property
    def name(self) -> str:
        return self._name

    @property
    def identifier(self) -> str:
        return f'openai/{self._model}'

    def generate(self, prompt: ChatThread) -> ChatStream:
        def _stream() -> ChatStream:
            if self._auth is not None:
                client = OpenAI(
                    api_key=self._auth
                )
            else:
                client = OpenAI()
            sanitized_prompt = self._binarization_format.binarize_chat(prompt)
            input_items = _encode_chat(sanitized_prompt)
            yield ChatIntent.RESPONSE

            # Use Any typecast because OpenAI expects a specific internal list of types
            kwargs: dict[str, Any] = {}
            if self._reasoning is not None:
                kwargs['reasoning'] = {"effort": self._reasoning}

            stream = client.responses.create(
                model=self._model,
                input=cast(Any, input_items),
                stream=True,
                **kwargs
            )
            for event in stream:
                if event.type == 'response.output_text.delta':
                    if event.delta:
                        yield event.delta
        return buffer_stream(_stream())

__all__ = [
    'OpenAIModel',
]
