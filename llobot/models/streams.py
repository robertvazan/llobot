from __future__ import annotations
import traceback
from typing import Iterable
from collections.abc import Callable
import threading
from queue import Queue
import llobot.text

type ModelStream = Iterable[str]

def text(response: str) -> ModelStream:
    """Creates a stream that yields a constant string."""
    if response:
        yield response

def ok(response: str) -> ModelStream:
    """Creates a success status stream with a checkmark prefix."""
    yield from text(f'✅ {response}')

def error(response: str) -> ModelStream:
    """Creates an error status stream with a cross mark prefix."""
    yield from text(f'❌ {response}')

def exception(ex: Exception) -> ModelStream:
    """Creates an error stream from an exception, including a stack trace."""
    message = str(ex) or ex.__class__.__name__
    stack_trace = "".join(traceback.format_exception(ex)).strip()
    details = llobot.text.details('Stack trace', '', stack_trace)
    yield from error(f'`{message}`\n\n{details}')

def buffer(stream: ModelStream) -> ModelStream:
    """
    Wraps a stream in a thread-safe queue.

    The queue is populated in a separate thread by iterating over the provided stream.
    The thread is started immediately when this function is called and terminates when iteration completes.
    This is useful for timely consumption of resources like network connections.
    If the iteration fails with an exception, this exception is propagated to the reader.
    """
    queue: Queue[str | None | Exception] = Queue()

    def worker():
        try:
            for item in stream:
                queue.put(item)
        except Exception as e:
            queue.put(e)
        finally:
            queue.put(None)

    threading.Thread(target=worker, daemon=True).start()

    while True:
        item = queue.get()
        if item is None:
            break
        if isinstance(item, Exception):
            raise item
        yield item

__all__ = [
    'ModelStream',
    'text',
    'ok',
    'error',
    'exception',
    'buffer',
]
