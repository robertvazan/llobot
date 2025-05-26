from __future__ import annotations

class ModelListener:
    # Blocks forever.
    def listen(self):
        raise NotImplementedError

def create(listen: Callable[[], None]):
    class LambdaListener:
        def listen(self):
            listen()
    return LambdaListener()

__all__ = [
    'ModelListener',
    'create',
]

