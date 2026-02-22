"""
A wrapper for models that retries on failure.
"""
from __future__ import annotations
import logging
import time
from typing import Iterable

from llobot.chats.stream import ChatStream
from llobot.chats.thread import ChatThread
from llobot.models import Model
from llobot.utils.values import ValueTypeMixin

logger = logging.getLogger(__name__)

class RetryingModel(Model, ValueTypeMixin):
    """
    A model wrapper that retries generation on failure.

    This wrapper implements a retry loop with specified delays. It buffers
    the output of the underlying model and only yields it if the generation
    completes successfully. If an exception occurs, the buffer is discarded,
    and the operation is retried after a delay.

    Motivation:
    This is particularly useful for unstable APIs like Gemini which often return
    503 or 500 errors. By catching these exceptions at a high level and retrying
    with exponential backoff, we can make the application more robust.
    """
    _model: Model
    _delays: tuple[float, ...]

    def __init__(self,
        model: Model,
        delays: Iterable[float] = (10, 20, 30, 60, 120, 180, 180),
    ):
        """
        Initializes the RetryingModel.

        Args:
            model: The underlying model to wrap.
            delays: A sequence of delays (in seconds) to wait between retries.
                    Defaults to (10, 20, 30, 60, 120, 180, 180), which roughly
                    follows a doubling pattern with some adjustments.
        """
        self._model = model
        self._delays = tuple(delays)

    @property
    def name(self) -> str:
        return self._model.name

    @property
    def identifier(self) -> str:
        return self._model.identifier

    def generate(self, prompt: ChatThread) -> ChatStream:
        """
        Generates a response, retrying on failure.

        It attempts to generate a response using the underlying model. If an
        exception occurs during generation (either immediately or while consuming
        the stream), the exception is logged, the process waits for the configured
        delay, and then retries.

        If all retries are exhausted, the final attempt is made without exception
        handling or buffering, allowing any errors to propagate to the caller.
        """
        for delay in self._delays:
            try:
                buffer = []
                # Buffer the entire stream.
                # If an exception occurs during iteration, it will be caught.
                for item in self._model.generate(prompt):
                    buffer.append(item)

                # If we get here, generation succeeded. Yield from buffer.
                yield from buffer
                return
            except Exception as e:
                logger.error(f"Model {self._model.name} failed (retrying in {delay}s): {e}", exc_info=True)
                time.sleep(delay)

        # Final attempt without buffering or exception handling.
        yield from self._model.generate(prompt)

    def _ephemeral_fields(self) -> Iterable[str]:
        return []

__all__ = [
    'RetryingModel',
]
