from __future__ import annotations
from pathlib import Path
import traceback
from llobot.chats import ChatIntent, ChatBranch
import llobot.text

class ModelStream:
    _response: str
    _done: bool

    def __init__(self):
        self._response = ''
        self._done = False

    # Returns next chunk. Returns None when the response is complete.
    def _receive(self) -> str | None:
        return None

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
        if item is None:
            self._done = True
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

    def __add__(self, second: ModelStream) -> ModelStream:
        first = self
        class ConcatenatedStream(ModelStream):
            _separated: bool
            def __init__(self):
                super().__init__()
                self._separated = False
            def _receive(self) -> str | None:
                token1 = first.receive()
                if token1 is not None:
                    return token1
                token2 = second.receive()
                if token2 is not None:
                    if not self._separated and first.response():
                        self._separated = True
                        token2 = '\n\n' + token2
                    return token2
                return None
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

def completed(response: str, *, chunk_size: int = 5000) -> ModelStream:
    class CompletedStream(ModelStream):
        _position: int
        def __init__(self):
            super().__init__()
            self._position = 0
        def _receive(self) -> str | None:
            if self._position >= len(response):
                return None
            chunk = response[self._position:self._position + chunk_size]
            self._position += len(chunk)
            return chunk
    return CompletedStream()

def status(response: str, **kwargs) -> ModelStream:
    return completed(response, **kwargs)

def ok(response: str) -> ModelStream:
    return status(f'✅ {response}')

def error(response: str) -> ModelStream:
    return status(f'❌ {response}')

def exception(ex: Exception) -> ModelStream:
    message = str(ex) or ex.__class__.__name__
    stack_trace = "".join(traceback.format_exception(ex)).strip()
    details = llobot.text.details('Stack trace', '', stack_trace)
    return error(f'{message}\n\n{details}')

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
            def _receive(self) -> str | None:
                token = stream.receive()
                if token is not None:
                    return token
                if not self._notified:
                    self._notified = True
                    callback(stream)
                return None
            def _close(self):
                stream.close()
        return NotifyStream()
    return filtered(apply)

def silence() -> ModelFilter:
    def apply(stream: ModelStream) -> ModelStream:
        class SilenceStream(ModelStream):
            def __init__(self):
                super().__init__()
            def _receive(self) -> str | None:
                stream.receive_all()
                return None
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
            def _receive(self) -> str | None:
                if self._failed:
                    return None
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
                return None
            def _close(self):
                stream.close()
        return HandlerStream()
    return filtered(apply)

def chat(prompt: ChatBranch, stream: ModelStream) -> ChatBranch:
    return prompt + ChatIntent.RESPONSE.message(stream.response())

__all__ = [
    'ModelStream',
    'ModelFilter',
    'completed',
    'status',
    'ok',
    'error',
    'exception',
    'filtered',
    'notify',
    'silence',
    'handler',
    'chat',
]
