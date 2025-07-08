from __future__ import annotations
from functools import cache
from llobot.roles import Role
from llobot.roles.requests import RoleRequest
import llobot.roles

class RoleWrapper:
    def wrap(self, role: Role) -> Role:
        return role

    def __call__(self, role: Role) -> Role:
        return self.wrap(role)

    def __or__(self, other: RoleWrapper) -> RoleWrapper:
        return create(lambda role: other(self(role)))

def create(function: Callable[[Role], Role]) -> RoleWrapper:
    class LambdaRoleWrapper(RoleWrapper):
        def wrap(self, role: Role) -> Role:
            return function(role)
    return LambdaRoleWrapper()

def stateless(function: Callable[[Role, RoleRequest], Context]) -> RoleWrapper:
    return create(lambda role: llobot.roles.create(lambda request: function(role, request)))

@cache
def standard() -> RoleWrapper:
    import llobot.roles.deltas
    return llobot.roles.deltas.standard()

__all__ = [
    'RoleWrapper',
    'create',
    'stateless',
    'standard',
]

