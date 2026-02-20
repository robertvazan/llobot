from __future__ import annotations
from typing import Iterable
from google import genai
from google.genai import types
from llobot.chats.intent import ChatIntent
from llobot.chats.thread import ChatThread
from llobot.models import Model
from llobot.chats.stream import ChatStream, buffer_stream
from llobot.formats.binarization import BinarizationFormat, standard_binarization_format
from llobot.utils.values import ValueTypeMixin

class GeminiModel(Model, ValueTypeMixin):
    """
    A model that uses the Google Gemini API.
    """
    _name: str
    _model: str
    _client: genai.Client
    _binarization_format: BinarizationFormat

    def __init__(self, *,
        model: str,
        name: str | None = None,
        client: genai.Client | None = None,
        auth: str | None = None,
        binarization_format: BinarizationFormat | None = None,
    ):
        """
        Initializes the Gemini model.

        Args:
            model: The model ID to use with the Gemini API. Mandatory.
            name: The name for this model instance in llobot. Defaults to model ID.
            client: An existing `genai.Client` instance. If not provided, a new one is created.
            auth: Your Google API key. If not provided, the `GOOGLE_API_KEY` environment
                  variable is used.
            binarization_format: Format to use for prompt binarization. Defaults to standard.
        """
        self._name = name if name is not None else model
        self._model = model
        if client:
            self._client = client
        elif auth:
            self._client = genai.Client(api_key=auth)
        else:
            # API key is taken from GOOGLE_API_KEY environment variable.
            self._client = genai.Client()
        self._binarization_format = binarization_format or standard_binarization_format()

    def _ephemeral_fields(self) -> Iterable[str]:
        return ['_client']

    @property
    def name(self) -> str:
        return self._name

    @property
    def identifier(self) -> str:
        return f'google/{self._model}'

    def generate(self, prompt: ChatThread) -> ChatStream:
        def _stream() -> ChatStream:
            contents = []
            sanitized_prompt = self._binarization_format.binarize_chat(prompt)
            for message in sanitized_prompt:
                if message.intent == ChatIntent.PROMPT:
                    contents.append(types.UserContent(parts=[types.Part.from_text(text=message.content)]))
                else:
                    contents.append(types.ModelContent(parts=[types.Part.from_text(text=message.content)]))
            config = types.GenerateContentConfig()
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
