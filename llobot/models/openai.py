"""
Client for OpenAI models.
"""
from __future__ import annotations
from typing import Iterable, cast
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionReasoningEffort, ChatCompletionRole
from llobot.formats.binarization import BinarizationFormat, standard_binarization_format
from llobot.chats.thread import ChatThread
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.models import Model
from llobot.chats.stream import ChatStream, buffer_stream
from llobot.utils.values import ValueTypeMixin

def _encode_role(intent: ChatIntent) -> ChatCompletionRole:
    if intent == ChatIntent.RESPONSE:
        return 'assistant'
    else:
        return 'user'

def _encode_message(message: ChatMessage) -> dict[str, str]:
    return {
        'role': _encode_role(message.intent),
        'content': message.content
    }

def _encode_chat(chat: ChatThread) -> list[ChatCompletionMessageParam]:
    return [cast(ChatCompletionMessageParam, _encode_message(message)) for message in chat]

class OpenAIModel(Model, ValueTypeMixin):
    """
    A model that uses the OpenAI API.
    """
    _name: str
    _model: str
    _auth: str
    _reasoning_effort: ChatCompletionReasoningEffort
    _binarization_format: BinarizationFormat

    def __init__(self, *,
        model: str,
        auth: str,
        name: str | None = None,
        reasoning_effort: ChatCompletionReasoningEffort = 'medium',
        binarization_format: BinarizationFormat | None = None,
    ):
        """
        Initializes the OpenAI model.

        Args:
            model: The model ID to use with the API. Mandatory.
            auth: The API key for OpenAI.
            name: The name for this model instance in llobot. Defaults to model ID.
            reasoning_effort: Reasoning effort for the model. Defaults to 'medium'.
            binarization_format: Format to use for prompt binarization. Defaults to standard.
        """
        self._name = name if name is not None else model
        self._model = model
        self._auth = auth
        self._reasoning_effort = reasoning_effort
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
            client = OpenAI(
                api_key=self._auth
            )
            sanitized_prompt = self._binarization_format.binarize_chat(prompt)
            messages = _encode_chat(sanitized_prompt)
            yield ChatIntent.RESPONSE
            completion = client.chat.completions.create(
                model=self._model,
                messages=messages,
                stream=True,
                reasoning_effort=self._reasoning_effort,
            )
            for chunk in completion:
                if chunk.choices:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content
        return buffer_stream(_stream())

__all__ = [
    'OpenAIModel',
]
