"""
Client for OpenAI models.
"""
from __future__ import annotations
from typing import Iterable
from openai import OpenAI
from llobot.chats.binarization import binarize_chat, binarize_intent
from llobot.chats.thread import ChatThread
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.models import Model
from llobot.chats.stream import ChatStream, buffer_stream
from llobot.utils.values import ValueTypeMixin

def _encode_role(intent: ChatIntent) -> str:
    if binarize_intent(intent) == ChatIntent.RESPONSE:
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
    _auth: str
    _context_budget: int
    _reasoning_effort: str

    def __init__(self, name: str, *,
        auth: str,
        model: str = 'gpt-5',
        context_budget: int = 100_000,
        reasoning_effort: str = 'medium',
    ):
        """
        Initializes the OpenAI model.

        Args:
            name: The name for this model instance in llobot.
            auth: The API key for OpenAI.
            model: The model ID to use with the API. Defaults to 'gpt-5'.
            context_budget: The character budget for context stuffing.
            reasoning_effort: Reasoning effort for the model. Defaults to 'medium'.
        """
        self._name = name
        self._model = model
        self._auth = auth
        self._context_budget = context_budget
        self._reasoning_effort = reasoning_effort

    def _ephemeral_fields(self) -> Iterable[str]:
        return ['_auth']

    @property
    def name(self) -> str:
        return self._name

    @property
    def context_budget(self) -> int:
        return self._context_budget

    def generate(self, prompt: ChatThread) -> ChatStream:
        def _stream() -> ChatStream:
            client = OpenAI(
                api_key=self._auth
            )
            sanitized_prompt = binarize_chat(prompt, last=ChatIntent.PROMPT)
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
