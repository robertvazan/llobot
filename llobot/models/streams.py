from __future__ import annotations
from pathlib import Path
import traceback
from llobot.chats import ChatIntent, ChatBranch
from llobot.models.stats import ModelStats

class ModelStream:
    _response: str
    _stats: ModelStats
    _done: bool

    def __init__(self):
        self._response = ''
        self._stats = ModelStats()
        self._done = False

    # Returns next chunk. Returns stats when the response is complete.
    def _receive(self) -> str | ModelStats:
        return ModelStats()

    # Must tolerate multiple close() calls. Must tolerate broken connection.
    def _close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self._close()

    def close(self):
        self._close()

    def receive(self) -> str | None:
        if self._done:
            return None
        item = self._receive()
        if isinstance(item, ModelStats):
            self._done = True
            self._stats = item
            return None
        self._response += item
        return item

    def receive_all(self):
        while not self._done:
            self.receive()

    def __iter__(self) -> Iterator[str]:
        while True:
            token = self.receive()
            if token is None:
                break
            yield token

    def response(self) -> str:
        self.receive_all()
        return self._response

    def stats(self) -> ModelStats:
        self.receive_all()
        return self._stats

    def __add__(self, second: ModelStream) -> ModelStream:
        first = self
        class ConcatenatedStream(ModelStream):
            _separated: bool
            def __init__(self):
                super().__init__()
                self._separated = False
            def _receive(self) -> str | ModelStats:
                token1 = first.receive()
                if token1:
                    return token1
                token2 = second.receive()
                if token2:
                    if not self._separated and first.response():
                        self._separated = True
                        token2 = '\n\n' + token2
                    return token2
                return first.stats() + second.stats()
            def _close(self):
                first._close()
                second._close()
        return ConcatenatedStream()

class ModelFilter:
    def apply(self, stream: ModelStream) -> ModelStream:
        return stream

    def __call__(self, stream: ModelStream) -> ModelStream:
        return self.apply(stream)

    def __ror__(self, stream: ModelStream) -> ModelStream:
        return self.apply(stream)

# This can be used to propagate stream via an exception instead of using function return.
class ModelException(Exception):
    stream: ModelStream

    def __init__(self, stream: ModelStream):
        self.stream = stream

def completed(response: str, *, stats: ModelStats = ModelStats()) -> ModelStream:
    class CompletedStream(ModelStream):
        _consumed: bool
        def __init__(self):
            super().__init__()
            self._consumed = False
        def _receive(self) -> str | ModelStats:
            if self._consumed:
                return stats
            self._consumed = True
            return response
    return CompletedStream()

def status(response: str, **kwargs) -> ModelStream:
    return completed(response, **kwargs)

def ok(response: str) -> ModelStream:
    return status(f'✅ {response}')

def error(response: str) -> ModelStream:
    return status(f'❌ {response}')

def exception(ex: Exception) -> ModelStream:
    if isinstance(ex,  ModelException):
        return ex.stream
    return error(f'Exception:\n\n```\n{"".join(traceback.format_exception(ex)).strip()}\n```')

def fail(response: str):
    raise ModelException(error(response))

def filtered(function: Callable[[ModelStream], ModelStream]) -> ModelFilter:
    class LambdaFilter(ModelFilter):
        def apply(self, stream: ModelStream) -> ModelStream:
            return function(stream)
    return LambdaFilter()

def notify(callback: Callable[[ModelStream], None]) -> ModelFilter:
    def apply(stream: ModelStream) -> ModelStream:
        class NotifyStream(ModelStream):
            _notified: bool
            def __init__(self):
                super().__init__()
                self._notified = False
            def _receive(self) -> str | ModelStats:
                token = stream.receive()
                if token is not None:
                    return token
                if not self._notified:
                    self._notified = True
                    callback(stream)
                return stream.stats()
            def _close(self):
                stream.close()
        return NotifyStream()
    return filtered(apply)

def silence() -> ModelFilter:
    def apply(stream: ModelStream) -> ModelStream:
        class SilenceStream(ModelStream):
            def __init__(self):
                super().__init__()
            def _receive(self) -> str | ModelStats:
                stream.receive_all()
                return stream.stats()
            def _close(self):
                stream.close()
        return SilenceStream()
    return filtered(apply)

def handler(*, callback: Callable[[], None] | None = None) -> ModelFilter:
    def apply(stream: ModelStream) -> ModelStream:
        class HandlerStream(ModelStream):
            _length: int
            _failed: bool
            def __init__(self):
                super().__init__()
                self._length = 0
                self._failed = False
            def _receive(self) -> str | ModelStats:
                if self._failed:
                    return ModelStats()
                try:
                    token = stream.receive()
                except Exception as ex:
                    self._failed = True
                    if callback:
                        callback()
                    separator = '\n\n' if self._length > 0 else ''
                    return separator + exception(ex).response()
                if token is not None:
                    self._length += len(token)
                    return token
                return stream.stats()
            def _close(self):
                stream.close()
        return HandlerStream()
    return filtered(apply)

def chat(prompt: ChatBranch, stream: ModelStream) -> ChatBranch:
    return prompt + ChatIntent.RESPONSE.message(stream.response())

__all__ = [
    'ModelStream',
    'ModelFilter',
    'ModelException',
    'completed',
    'status',
    'ok',
    'error',
    'exception',
    'fail',
    'filtered',
    'notify',
    'silence',
    'handler',
    'chat',
]

