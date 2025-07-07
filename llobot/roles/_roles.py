from __future__ import annotations
from functools import cache
from llobot.contexts import Context
import llobot.contexts

class Role:
    # Returns the synthetic part of the prompt that is prepended to the user prompt.
    def stuff(self, request: 'RoleRequest') -> Context:
        return llobot.contexts.empty()

    def __call__(self, request: 'RoleRequest') -> Context:
        return self.stuff(request)

    def __add__(self, other: Role) -> Role:
        from llobot.roles.requests import RoleRequest
        def stuff(request: RoleRequest):
            first = self(request)
            second = other(request.replace(budget=request.budget-first.cost, context=request.context+first))
            return first + second
        return create(stuff)

    def __mul__(self, other: float) -> Role:
        import llobot.roles.wrappers
        return self | llobot.roles.wrappers.limit(other)

    def __rmul__(self, other: float) -> Role:
        return self * other

    def __or__(self, wrapper: 'RoleWrapper') -> Role:
        return wrapper(self)

def create(function: Callable[['RoleRequest'], Context]) -> Role:
    from llobot.roles.requests import RoleRequest
    class LambdaRole(Role):
        def stuff(self, request: RoleRequest) -> Context:
            return function(request)
    return LambdaRole()

@cache
def empty() -> Role:
    return Role()

__all__ = [
    'Role',
    'create',
    'empty',
]

