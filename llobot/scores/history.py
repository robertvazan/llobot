from __future__ import annotations
import heapq
from llobot.chats import ChatBranch
from llobot.scores.decays import DecayScores
import llobot.scores.decays

class HistoryScores:
    def __iter__(self) -> Iterator[tuple(float, ChatBranch)]:
        raise NotImplementedError

    def chats(self) -> Iterable[ChatBranch]:
        for score, chat in self:
            yield chat

    def __add__(self, other: float | int | DecayScores) -> HistoryScores:
        if isinstance(other, (float, int)):
            return create(lambda: ((score + other, chat) for score, chat in self))
        if isinstance(other, DecayScores):
            return create(lambda: ((score + decay, chat) for (score, chat), decay in zip(self, other)))
        raise TypeError(other)

    def __radd__(self, other: float | int) -> HistoryScores:
        return self + other

    def __neg__(self) -> HistoryScores:
        return create(lambda: ((-score, chat) for score, chat in self))

    def __sub__(self, other: float | int | DecayScores) -> HistoryScores:
        return self + (-other)

    def __rsub__(self, other: float | int) -> HistoryScores:
        return (-self) + other

    def __mul__(self, other: float | int | DecayScores) -> HistoryScores:
        if isinstance(other, (float, int)):
            return create(lambda: ((score * other, chat) for score, chat in self))
        if isinstance(other, DecayScores):
            return create(lambda: ((score * decay, chat) for (score, chat), decay in zip(self, other)))
        raise TypeError(other)

    def __rmul__(self, other: float | int) -> HistoryScores:
        return self * other

    def __truediv__(self, other: float | int | DecayScores) -> HistoryScores:
        if isinstance(other, (float, int)):
            return create(lambda: ((score / other, chat) for score, chat in self))
        if isinstance(other, DecayScores):
            return create(lambda: ((score / decay, chat) for (score, chat), decay in zip(self, other)))
        raise TypeError(other)

    def __rtruediv__(self, other: float | int) -> HistoryScores:
        return create(lambda: ((other / score, chat) for score, chat in self))

def create(constructor: Callable[[], Iterable[tuple[float, ChatBranch]]]) -> HistoryScores:
    class LambdaHistoryScores(HistoryScores):
        def __iter__(self) -> Iterator[tuple[float, ChatBranch]]:
            return iter(constructor())
    return LambdaHistoryScores()

def decay(chats: Iterable[ChatBranch], scores: DecayScores = llobot.scores.decays.standard()) -> HistoryScores:
    return create(lambda: zip(scores, chats))

def constant(chats: Iterable[ChatBranch], value: float | int = 1) -> HistoryScores:
    return decay(chats, llobot.scores.decays.constant(value))

def zipf(chats: Iterable[ChatBranch]) -> HistoryScores:
    return decay(chats, llobot.scores.decays.zipf())

def exponential(chats: Iterable[ChatBranch], factor: float = 0.5) -> HistoryScores:
    return decay(chats, llobot.scores.decays.exponential(factor))

# Best effort sorting up to the specified depth.
def ascending(source: HistoryScores, depth: int = 10) -> HistoryScores:
    def generate():
        heap = []
        for index, (score, chat) in enumerate(source):
            # Index is added to disambiguate equal scores, so that heapq does not attempt to compare chats.
            heapq.heappush(heap, (score, index, chat))
            if len(heap) >= depth:
                score, _, chat = heapq.heappop(heap)
                yield score, chat
        while heap:
            score, _, chat = heapq.heappop(heap)
            yield score, chat
    return create(lambda: generate())

def descending(source: HistoryScores, depth: int = 10) -> HistoryScores:
    return -ascending(-source, depth)

# Merges semi-sorted sources into single sequence in best effort descending order.
def merge(*sources: HistoryScores) -> HistoryScores:
    def generate():
        iterators = [iter(s) for s in sources]
        heap = []
        for index, source in enumerate(sources):
            iterator = iter(source)
            try:
                score, chat = next(iterator)
                # We have to include index in the tuple to break score ties that would otherwise cause Python to compare chats.
                heapq.heappush(heap, (-score, index, chat, iterator))
            except StopIteration:
                pass
        while heap:
            score, index, chat, iterator = heapq.heappop(heap)
            yield -score, chat
            try:
                score, chat = next(iterator)
                heapq.heappush(heap, (-score, index, chat, iterator))
            except StopIteration:
                pass
    return create(lambda: generate())

__all__ = [
    'HistoryScores',
    'create',
    'decay',
    'constant',
    'zipf',
    'exponential',
    'ascending',
    'descending',
    'merge',
]

