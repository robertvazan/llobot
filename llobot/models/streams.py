from __future__ import annotations
import traceback
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

def text(response: str) -> ModelStream:
    """Creates a stream that yields a constant string."""
    class TextStream(ModelStream):
        _sent: bool
        def __init__(self):
            super().__init__()
            self._sent = False
        def _receive(self) -> str | None:
            if self._sent or not response:
                return None
            self._sent = True
            return response
    return TextStream()

def ok(response: str) -> ModelStream:
    """Creates a success status stream with a checkmark prefix."""
    return text(f'✅ {response}')

def error(response: str) -> ModelStream:
    """Creates an error status stream with a cross mark prefix."""
    return text(f'❌ {response}')

def exception(ex: Exception) -> ModelStream:
    """Creates an error stream from an exception, including a stack trace."""
    message = str(ex) or ex.__class__.__name__
    stack_trace = "".join(traceback.format_exception(ex)).strip()
    details = llobot.text.details('Stack trace', '', stack_trace)
    return error(f'`{message}`\n\n{details}')

__all__ = [
    'ModelStream',
    'text',
    'ok',
    'error',
    'exception',
]
