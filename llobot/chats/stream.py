"""
ChatStream is a stream of tokens that can represent one or more messages.

A ChatStream is an iterable of `str` and `ChatIntent` objects.
String chunks are concatenated to form message content. `ChatIntent` objects
mark the beginning of a new message.

- Every stream must start with an `ChatIntent` unless the stream is empty.
- A new message starts when a `ChatIntent` is yielded.
- A message ends when a new `ChatIntent` is yielded or the stream ends.
- Empty messages are possible (two `ChatIntent`s in a row).
- It is possible for two consecutive messages to have the same intent.
"""

from __future__ import annotations
import threading
from queue import Queue
from typing import Iterable
from llobot.chats.intent import ChatIntent

type ChatStream = Iterable[str | ChatIntent]

def buffer_stream(stream: ChatStream) -> ChatStream:
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
    'ChatStream',
    'buffer_stream',
]
