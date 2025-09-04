from __future__ import annotations
from collections.abc import Callable

class ModelListener:
    # Blocks forever.
    def listen(self):
        raise NotImplementedError

def create_listener(listen: Callable[[], None]):
    class LambdaListener:
        def listen(self):
            listen()
    return LambdaListener()

__all__ = [
    'ModelListener',
    'create_listener',
]
