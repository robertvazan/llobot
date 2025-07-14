from __future__ import annotations
import math
from functools import cache
from zlib import crc32
import llobot.time
from llobot.chats import ChatRole, ChatBranch

class ChatScorer:
    def score(self, chat: ChatBranch) -> float:
        return 0

    def __call__(self, chat: ChatBranch) -> float:
        return self.score(chat)

    @staticmethod
    def _coerce_operand(other: ChatScorer | float | int) -> ChatScorer:
        if isinstance(other, (int, float)):
            return constant(other)
        return other

    def __add__(self, other: ChatScorer | float | int) -> ChatScorer:
        other = self._coerce_operand(other)
        return create(lambda chat: self(chat) + other(chat))

    def __radd__(self, other: float | int) -> ChatScorer:
        return self + other

    def __sub__(self, other: ChatScorer | float | int) -> ChatScorer:
        other = self._coerce_operand(other)
        return create(lambda chat: self(chat) - other(chat))

    def __rsub__(self, other: float | int) -> ChatScorer:
        return self._coerce_operand(other) - self

    def __neg__(self) -> DecayScores:
        return 0 - self

    def __mul__(self, other: ChatScorer | float | int) -> ChatScorer:
        other = self._coerce_operand(other)
        return create(lambda chat: self(chat) * other(chat))

    def __rmul__(self, other: float | int) -> ChatScorer:
        return self * other

    def __truediv__(self, other: ChatScorer | float | int) -> ChatScorer:
        other = self._coerce_operand(other)
        return create(lambda chat: self(chat) / other(chat))

    def __rtruediv__(self, other: float | int) -> ChatScorer:
        return self._coerce_operand(other) / self

def create(function: Callable[[ChatBranch], float | int]) -> ChatScorer:
    class LambdaChatScorer(ChatScorer):
        def score(self, chat: ChatBranch) -> float:
            return float(function(chat))
    return LambdaChatScorer()

@cache
def constant(score: float | int = 1) -> ChatScorer:
    return create(lambda _: score)

@cache
def length() -> ChatScorer:
    return create(lambda chat: chat.cost)

@cache
def sqrt_length() -> ChatScorer:
    return create(lambda chat: math.sqrt(chat.cost))

@cache
def response_length() -> ChatScorer:
    return create(lambda chat: sum([len(message.content) for message in chat if message.role == ChatRole.ASSISTANT]))

@cache
def response_share() -> ChatScorer:
    return response_length() / length()

@cache
def random() -> ChatScorer:
    return create(lambda chat: crc32(chat.monolithic().encode('utf-8')) or 1)

@cache
def standard() -> ChatScorer:
    # Use square root of chat length to invest available budget evenly to both chat diversity and chat length (which minimizes per-chat overhead).
    return response_share() / sqrt_length()

__all__ = [
    'ChatScorer',
    'create',
    'constant',
    'length',
    'sqrt_length',
    'response_length',
    'response_share',
    'random',
    'standard',
]

