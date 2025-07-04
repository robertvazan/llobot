from __future__ import annotations
from functools import cache
from llobot.experts import Expert
from llobot.experts.requests import ExpertRequest
import llobot.experts

class ExpertWrapper:
    def wrap(self, expert: Expert) -> Expert:
        return expert

    def __call__(self, expert: Expert) -> Expert:
        return self.wrap(expert)

    def __or__(self, other: ExpertWrapper) -> ExpertWrapper:
        return create(lambda expert: other(self(expert)))

def create(function: Callable[[Expert], Expert]) -> ExpertWrapper:
    class LambdaExpertWrapper(ExpertWrapper):
        def wrap(self, expert: Expert) -> Expert:
            return function(expert)
    return LambdaExpertWrapper()

def stateless(function: Callable[[Expert, ExpertRequest], Context]) -> ExpertWrapper:
    return create(lambda expert: llobot.experts.create(lambda request: function(expert, request)))

@cache
def limit(share: float) -> ExpertWrapper:
    return stateless(lambda expert, request: expert(request.replace(budget=int(share*request.budget))))

@cache
def standard() -> ExpertWrapper:
    import llobot.experts.deltas
    return llobot.experts.deltas.standard()

__all__ = [
    'ExpertWrapper',
    'create',
    'stateless',
    'limit',
    'standard',
]

