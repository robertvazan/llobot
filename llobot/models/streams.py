"""
ModelStream is a stream of tokens that can represent one or more messages.

A ModelStream is an iterable of `str` and `ChatIntent` objects.
String chunks are concatenated to form message content. `ChatIntent` objects
mark the beginning of a new message.

- If the stream starts with a `str`, the first message is implicitly of
  `ChatIntent.RESPONSE` intent.
- A new message starts when a `ChatIntent` is yielded.
- A message ends when a new `ChatIntent` is yielded or the stream ends.
- Empty messages are possible (two `ChatIntent`s in a row).
- It is possible for two consecutive messages to have the same intent.

Code that consumes streams and only expects a single message can simply
filter out `ChatIntent` objects and concatenate the strings.
"""

from __future__ import annotations
import traceback
from typing import Iterable
from collections.abc import Callable
import threading
from queue import Queue
import llobot.text
from llobot.chats.intents import ChatIntent
from llobot.chats.messages import ChatMessage

type ModelStream = Iterable[str | ChatIntent]

def text(response: str) -> ModelStream:
    """Creates a stream that yields a constant string."""
    if response:
        yield response

def message(msg: ChatMessage) -> ModelStream:
    """Creates a stream that yields a single message."""
    yield msg.intent
    if msg.content:
        yield msg.content

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
    queue: Queue[str | ChatIntent | None | Exception] = Queue()

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
    'message',
    'ok',
    'error',
    'exception',
    'buffer',
]
