from __future__ import annotations
from google import genai
from google.genai import types
from llobot.chats import ChatRole, ChatBranch
from llobot.models import Model
from llobot.models.streams import ModelStream
from llobot.models.stats import ModelStats
from llobot.models.estimators import TokenLengthEstimator
import llobot.models.openai
import llobot.models.estimators

class _GeminiStream(ModelStream):
    _iterator: Iterator[str]

    def __init__(self,
        client: genai.Client,
        model: str,
        prompt: ChatBranch,
    ):
        super().__init__()
        self._iterator = iter(self._iterate(client, model, prompt))

    def _iterate(self,
        client: genai.Client,
        model: str,
        prompt: ChatBranch,
    ) -> Iterable[str]:
        contents = []
        for message in prompt:
            if message.role == ChatRole.USER:
                contents.append(types.UserContent(parts=[types.Part(text=message.content)]))
            else:
                contents.append(types.ModelContent(parts=[types.Part(text=message.content)]))
        stream = client.models.generate_content_stream(
            model=model,
            contents=contents
        )
        for chunk in stream:
            if chunk.text:
                yield chunk.text

    def _receive(self) -> str | ModelStats:
        try:
            return next(self._iterator)
        except StopIteration:
            return ModelStats()

class _GeminiModel(Model):
    _client: genai.Client
    _name: str
    _aliases: list[str]
    _context_size: int
    _estimator: TokenLengthEstimator

    def __init__(self, name: str, context_size: int, *,
        client: genai.Client | None = None,
        auth: str | None = None,
        aliases: Iterable[str] = [],
        estimator: TokenLengthEstimator = llobot.models.estimators.standard(),
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
        self._context_size = context_size
        self._estimator = estimator

    @property
    def name(self) -> str:
        return f'gemini/{self._name}'

    @property
    def aliases(self) -> Iterable[str]:
        yield self._name
        yield from self._aliases

    @property
    def options(self) -> dict:
        return {
            'context_size': self._context_size,
        }

    def validate_options(self, options: dict):
        allowed = {'context_size'}
        for unrecognized in set(options) - allowed:
            raise ValueError(f"Unrecognized option: {unrecognized}")

    def configure(self, options: dict) -> Model:
        return _GeminiModel(
            self._name,
            int(options.get('context_size', self._context_size)),
            client=self._client,
            aliases=self._aliases,
            estimator=self._estimator,
        )

    @property
    def context_size(self) -> int:
        return self._context_size

    @property
    def estimator(self) -> TokenLengthEstimator:
        return self._estimator

    def _connect(self, prompt: ChatBranch) -> ModelStream:
        return _GeminiStream(
            self._client,
            self._name,
            prompt,
        )

def create(name: str, context_size: int, **kwargs) -> Model:
    return _GeminiModel(name, context_size, **kwargs)

def via_openai_protocol(name: str, context_size: int, auth: str, **kwargs) -> Model:
    return llobot.models.openai.compatible('https://generativelanguage.googleapis.com/v1beta/openai', 'gemini', name, context_size, auth=auth, **kwargs)

__all__ = [
    'create',
    'via_openai_protocol',
]

