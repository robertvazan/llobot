from __future__ import annotations
from google import genai
from google.genai import types
from llobot.chats import ChatRole, ChatBranch
from llobot.models import Model
from llobot.models.streams import ModelStream
import llobot.models.openai
import llobot.models.streams

class _GeminiStream(ModelStream):
    _iterator: Iterator[str]

    def __init__(self,
        client: genai.Client,
        model: str,
        prompt: ChatBranch,
        thinking: int | None = None,
    ):
        super().__init__()
        self._iterator = self._iterate(client, model, prompt, thinking)

    def _iterate(self,
        client: genai.Client,
        model: str,
        prompt: ChatBranch,
        thinking: int | None = None,
    ) -> Iterable[str]:
        contents = []
        for message in prompt:
            if message.role == ChatRole.USER:
                contents.append(types.UserContent(parts=[types.Part(text=message.content)]))
            else:
                contents.append(types.ModelContent(parts=[types.Part(text=message.content)]))
        config = types.GenerateContentConfig()
        if thinking is not None:
            config.thinking_config = types.ThinkingConfig(thinking_budget=thinking)
        stream = client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=config,
        )
        for chunk in stream:
            if chunk.text:
                yield chunk.text

    def _receive(self) -> str | None:
        try:
            return next(self._iterator)
        except StopIteration:
            return None

class _GeminiModel(Model):
    _client: genai.Client
    _name: str
    _aliases: list[str]
    _context_budget: int
    _thinking: int | None

    def __init__(self, name: str, *,
        client: genai.Client | None = None,
        auth: str | None = None,
        aliases: Iterable[str] = [],
        context_budget: int = 100_000,
        thinking: int | None = None,
    ):
        if client:
            self._client = client
        elif auth:
            self._client = genai.Client(api_key=auth)
        else:
            # API key is taken from GOOGLE_API_KEY environment variable.
            self._client = genai.Client()
        self._name = name
        self._aliases = list(aliases)
        self._context_budget = context_budget
        self._thinking = thinking

    @property
    def name(self) -> str:
        return f'gemini/{self._name}'

    @property
    def aliases(self) -> Iterable[str]:
        yield self._name
        yield from self._aliases

    @property
    def options(self) -> dict:
        options = {
            'context_budget': self._context_budget,
        }
        if self._thinking is not None:
            options['thinking'] = self._thinking
        return options

    def validate_options(self, options: dict):
        allowed = {'context_budget', 'thinking'}
        for unrecognized in set(options) - allowed:
            raise ValueError(f"Unrecognized option: {unrecognized}")

    def configure(self, options: dict) -> Model:
        thinking = options.get('thinking', self._thinking)
        return _GeminiModel(
            self._name,
            client=self._client,
            aliases=self._aliases,
            context_budget=int(options.get('context_budget', self._context_budget)),
            thinking=int(thinking) if thinking else None,
        )

    @property
    def context_budget(self) -> int:
        return self._context_budget

    def generate(self, prompt: ChatBranch) -> ModelStream:
        return _GeminiStream(
            self._client,
            self._name,
            prompt,
            self._thinking,
        )

def create(name: str, **kwargs) -> Model:
    return _GeminiModel(name, **kwargs)

def via_openai_protocol(name: str, auth: str, **kwargs) -> Model:
    return llobot.models.openai.compatible('https://generativelanguage.googleapis.com/v1beta/openai', 'gemini', name, auth=auth, **kwargs)

__all__ = [
    'create',
    'via_openai_protocol',
]

