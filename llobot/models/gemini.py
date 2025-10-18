from __future__ import annotations
from typing import Iterable
from google import genai
from google.genai import types
from llobot.chats.intent import ChatIntent
from llobot.chats.thread import ChatThread
from llobot.models import Model
from llobot.models.streams import ModelStream, buffer_stream
from llobot.chats.binarization import binarize_chat
from llobot.utils.values import ValueTypeMixin

class GeminiModel(Model, ValueTypeMixin):
    """
    A model that uses the Google Gemini API.
    """
    _name: str
    _model: str
    _client: genai.Client
    _context_budget: int
    _thinking: int | None

    def __init__(self, name: str, *,
        model: str = 'gemini-2.5-pro',
        client: genai.Client | None = None,
        auth: str | None = None,
        context_budget: int = 100_000,
        thinking: int | None = None,
    ):
        """
        Initializes the Gemini model.

        Args:
            name: The name for this model instance in llobot.
            model: The model ID to use with the Gemini API. Defaults to 'gemini-2.5-pro'.
            client: An existing `genai.Client` instance. If not provided, a new one is created.
            auth: Your Google API key. If not provided, the `GOOGLE_API_KEY` environment
                  variable is used.
            context_budget: The character budget for context stuffing.
            thinking: The budget in tokens to allocate for "thinking" (prompt construction).
        """
        self._name = name
        self._model = model
        if client:
            self._client = client
        elif auth:
            self._client = genai.Client(api_key=auth)
        else:
            # API key is taken from GOOGLE_API_KEY environment variable.
            self._client = genai.Client()
        self._context_budget = context_budget
        self._thinking = thinking

    def _ephemeral_fields(self) -> Iterable[str]:
        return ['_client']

    @property
    def name(self) -> str:
        return self._name

    @property
    def context_budget(self) -> int:
        return self._context_budget

    def generate(self, prompt: ChatThread) -> ModelStream:
        def _stream() -> ModelStream:
            contents = []
            sanitized_prompt = binarize_chat(prompt, last=ChatIntent.PROMPT)
            for message in sanitized_prompt:
                if message.intent == ChatIntent.PROMPT:
                    contents.append(types.UserContent(parts=[types.Part(text=message.content)]))
                else:
                    contents.append(types.ModelContent(parts=[types.Part(text=message.content)]))
            config = types.GenerateContentConfig()
            if self._thinking is not None:
                config.thinking_config = types.ThinkingConfig(thinking_budget=self._thinking)
            yield ChatIntent.RESPONSE
            stream = self._client.models.generate_content_stream(
                model=self._model,
                contents=contents,
                config=config,
            )
            for chunk in stream:
                if chunk.text:
                    yield chunk.text
        return buffer_stream(_stream())

__all__ = [
    'GeminiModel',
]
