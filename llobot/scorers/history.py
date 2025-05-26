from __future__ import annotations
from functools import cache, lru_cache
from llobot.chats import ChatBranch
from llobot.scores.decays import DecayScores
from llobot.scores.history import HistoryScores
from llobot.scorers.chats import ChatScorer
import llobot.scores.decays
import llobot.scores.history
import llobot.scorers.chats

class HistoryScorer:
    def score(self, chats: Iterable[ChatBranch]) -> HistoryScores:
        raise NotImplementedError

    def __call__(self, chats: Iterable[ChatBranch]) -> HistoryScores:
        return self.score(chats)

    def __add__(self, other: float | int | DecayScores) -> HistoryScorer:
        return create(lambda chats: self(chats) + other)

    def __radd__(self, other: float | int) -> HistoryScorer:
        return self + other

    def __neg__(self) -> HistoryScorer:
        return create(lambda chats: -self(chats))

    def __sub__(self, other: float | int | DecayScores) -> HistoryScorer:
        return self + (-other)

    def __rsub__(self, other: float | int) -> HistoryScorer:
        return (-self) + other

    def __mul__(self, other: float | int | DecayScores) -> HistoryScorer:
        return create(lambda chats: self(chats) * other)

    def __rmul__(self, other: float | int) -> HistoryScorer:
        return self * other

    def __truediv__(self, other: float | int | DecayScores) -> HistoryScorer:
        return self * (1 / other)

    def __rtruediv__(self, other: float | int) -> HistoryScorer:
        return create(lambda chats: other / self(chats))

def create(function: Callable[[Iterable[ChatBranch]], HistoryScores]) -> HistoryScorer:
    class LambdaHistoryScorer(HistoryScorer):
        def score(self, chats: Iterable[ChatBranch]) -> HistoryScores:
            return function(chats)
    return LambdaHistoryScorer()

@lru_cache
def decay(scores: DecayScores = llobot.scores.decays.standard()) -> HistoryScorer:
    return create(lambda chats: llobot.scores.history.decay(chats, scores))

@cache
def constant(value: float | int = 1) -> HistoryScorer:
    return create(lambda chats: llobot.scores.history.constant(chats, value))

@cache
def zipf() -> HistoryScorer:
    return create(lambda chats: llobot.scores.history.zipf(chats))

@cache
def exponential(factor: float = 0.5) -> HistoryScorer:
    return create(lambda chats: llobot.scores.history.exponential(chats, factor))

@lru_cache
def stateless(scorer: ChatScorer = llobot.scorers.chats.standard()) -> HistoryScorer:
    return create(lambda chats: llobot.scores.history.create(lambda: ((scorer(chat), chat) for chat in chats)))

@cache
def length() -> HistoryScorer:
    return stateless(llobot.scorers.chats.length())

@cache
def sqrt_length() -> HistoryScorer:
    return stateless(llobot.scorers.chats.sqrt_length())

@cache
def response_length() -> HistoryScorer:
    return stateless(llobot.scorers.chats.response_length())

@cache
def response_share() -> HistoryScorer:
    return stateless(llobot.scorers.chats.response_share())

@lru_cache
def ascending(scorer: HistoryScorer, depth: int = 10) -> HistoryScorer:
    return create(lambda chats: llobot.scores.history.ascending(scorer(chats), depth))

@lru_cache
def descending(scorer: HistoryScorer, depth: int = 10) -> HistoryScorer:
    return create(lambda chats: llobot.scores.history.descending(scorer(chats), depth))

@cache
def standard() -> HistoryScorer:
    # Use square root of chat length to invest available budget evenly to both chat diversity and chat length (which minimizes per-chat overhead).
    return descending(llobot.scores.decays.standard() * stateless())

__all__ = [
    'HistoryScorer',
    'create',
    'decay',
    'constant',
    'zipf',
    'exponential',
    'stateless',
    'length',
    'sqrt_length',
    'response_length',
    'response_share',
    'ascending',
    'descending',
    'standard',
]

