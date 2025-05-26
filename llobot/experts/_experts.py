from __future__ import annotations
from functools import cache
from llobot.contexts import Context
import llobot.contexts

class Expert:
    # Returns the synthetic part of the prompt that is prepended to the user prompt.
    def stuff(self, request: 'ExpertRequest') -> Context:
        return llobot.contexts.empty()

    def __call__(self, request: 'ExpertRequest') -> Context:
        return self.stuff(request)

    def __add__(self, other: Expert) -> Expert:
        from llobot.experts.requests import ExpertRequest
        def stuff(request: ExpertRequest):
            first = self(request)
            second = other(request.replace(budget=request.budget-first.cost, context=request.context+first))
            return first + second
        return create(stuff)

    def __mul__(self, other: float) -> Expert:
        import llobot.experts.wrappers
        return self | llobot.experts.wrappers.limit(other)

    def __rmul__(self, other: float) -> Expert:
        return self * other

    def __or__(self, wrapper: 'ExpertWrapper') -> Expert:
        return wrapper(self)

def create(function: Callable[['ExpertRequest'], Context]) -> Expert:
    from llobot.experts.requests import ExpertRequest
    class LambdaExpert(Expert):
        def stuff(self, request: ExpertRequest) -> Context:
            return function(request)
    return LambdaExpert()

@cache
def empty() -> Expert:
    return Expert()

__all__ = [
    'Expert',
    'create',
    'empty',
]

