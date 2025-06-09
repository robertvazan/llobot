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

# By default, reserve at least 20% of the budget to create sufficient margin for error in token length estimates.
# As for the reserved char count, that's the expected maximum context consumption for an article-long response, possibly in non-English language.
# We will however avoid adding the two reservations up, because it's exceedingly unlikely we get worst-case conditions in both response length and token length estimates.
@cache
def reserve(chars: int = 25_000, share: float = 0.2) -> ExpertWrapper:
    def stuff(expert: Expert, request: ExpertRequest) -> Context:
        # User prompts can be very long and they usually result in comparably long responses.
        # We will therefore subtract prompt length from the budget here, so that it does not eat into space reserved for the response and/or token length inaccuracies.
        reservation = max(chars, int(share * request.budget)) + request.prompt.cost
        # Limit reserved budget to 50% of the total budget, so that it does not eat (nearly) the whole budget.
        # This is particularly important when token length estimator is not initialized and returns a tiny pessimistic estimates.
        reasonable_reservation = min(reservation, request.budget // 2)
        return expert(request.replace(budget=request.budget-reasonable_reservation))
    return stateless(stuff)

@cache
def standard() -> ExpertWrapper:
    import llobot.experts.deltas
    return llobot.experts.deltas.standard() | reserve()

__all__ = [
    'ExpertWrapper',
    'create',
    'stateless',
    'limit',
    'reserve',
    'standard',
]

