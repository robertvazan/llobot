from __future__ import annotations
from llobot.chats import ChatBranch
import llobot.text

class Model:
    # Name must be globally unique, something like ollama/model-name:tag.
    # Model name should not include endpoint, because every sane setup will access given model only over single path.
    @property
    def name(self) -> str:
        raise NotImplementedError

    @property
    def dashed_name(self) -> str:
        return llobot.text.dashed_name(self.name)

    # Shorter names that are not necessarily unique.
    @property
    def aliases(self) -> Iterable[str]:
        return []

    def __str__(self) -> str:
        return self.name

    # Options should be a flat dict with string keys and JSON-serializable values (str, int, float, bool).
    @property
    def options(self) -> dict:
        return {}

    # Raises an exception on unexpected options or unexpected option values.
    def validate_options(self, options: dict):
        pass

    # Coerces the options and merges them with defaults, producing a new model that has the merged options as its defaults.
    # Uncoerced options can have string values, empty on None values for clearing, invalid values, and extraneous keys.
    def configure(self, options: dict) -> Model:
        return self

    # Number of tokens to use for context stuffing. This is a cost-benefit decision rather than an inherent model limit.
    @property
    def context_budget(self) -> int:
        raise NotImplementedError

    @property
    def estimator(self) -> 'TokenLengthEstimator':
        import llobot.models.estimators
        # Rely on standard() estimator being cached, so that its internal deadband and logging memory
        # is not reset every time this property is read.
        return llobot.models.estimators.standard()

    # Stream may be either returned from the function or thrown as ModelException.
    def _connect(self, prompt: ChatBranch) -> 'ModelStream':
        raise NotImplementedError

    @property
    def __estimator(self) -> 'TokenLengthEstimator':
        import llobot.models.estimators
        return llobot.models.estimators.prefixed(self.dashed_name + '-', self.estimator)

    def generate(self, prompt: ChatBranch, zone: str = '') -> 'ModelStream':
        from llobot.models.streams import ModelException
        import llobot.models.streams
        try:
            if not zone:
                return self._connect(prompt)
            return self._connect(prompt) | llobot.models.streams.notify(lambda stream: self.__estimator.update(zone, stream.stats()))
        except ModelException as ex:
            return ex.stream

    def estimate_token_length(self, zone: str) -> float:
        return self.__estimator.estimate(zone)

def echo(*, context_budget: int = 25_000, token_length: float = 0.0, aliases: Iterable[str] = []) -> Model:
    from llobot.models.streams import ModelStream
    from llobot.models.estimators import TokenLengthEstimator
    from llobot.models.stats import ModelStats
    import llobot.models.streams
    import llobot.models.estimators
    token_length = token_length or llobot.models.estimators.OPTIMISTIC_TOKEN_LENGTH
    class EchoModel(Model):
        _context_budget: int
        _token_length: float
        def __init__(self, context_budget: int, token_length: float):
            self._context_budget = context_budget
            self._token_length = token_length
        @property
        def name(self) -> str:
            return 'echo'
        @property
        def aliases(self) -> Iterable[str]:
            yield f'echo:{self._context_budget // 1024}k'
            yield from aliases
        @property
        def options(self) -> dict:
            return {
                'context_budget': self._context_budget,
                'token_length': self._token_length,
            }
        def validate_options(self, options: dict):
            allowed = {'context_budget', 'token_length'}
            for unrecognized in set(options) - allowed:
                raise ValueError(f"Unrecognized option: {unrecognized}")
        def configure(self, options: dict) -> Model:
            return EchoModel(
                int(options.get('context_budget', self._context_budget)),
                float(options.get('token_length', self._token_length)),
            )
        @property
        def context_budget(self) -> int:
            return self._context_budget
        @property
        def estimator(self) -> TokenLengthEstimator:
            return llobot.models.estimators.constant(self._token_length)
        def _connect(self, prompt: ChatBranch) -> ModelStream:
            return llobot.models.streams.completed(prompt.monolithic(), stats=ModelStats(total_chars=2*prompt.cost))
    return EchoModel(context_budget, token_length)

__all__ = [
    'Model',
    'echo',
]

