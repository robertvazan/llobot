from __future__ import annotations
from datetime import datetime
from llobot.projects import Project
from llobot.contexts import Context
from llobot.chats import ChatBranch
from llobot.roles.memory import RoleMemory
import llobot.contexts

class RoleRequest:
    _memory: RoleMemory
    _prompt: ChatBranch
    _project: Project | None
    _cutoff: datetime
    _budget: int

    def __init__(self, *,
        memory: RoleMemory,
        prompt: ChatBranch,
        project: Project | None = None,
        cutoff: datetime,
        budget: int,
    ):
        self._memory = memory
        self._prompt = prompt
        self._project = project
        self._cutoff = cutoff
        self._budget = budget

    @property
    def memory(self) -> RoleMemory:
        return self._memory

    @property
    def prompt(self) -> ChatBranch:
        return self._prompt

    @property
    def project(self) -> Project | None:
        return self._project

    @property
    def cutoff(self) -> datetime:
        return self._cutoff

    @property
    def budget(self) -> int:
        return self._budget

    def replace(self, **kwargs) -> RoleRequest:
        return RoleRequest(**({key[1:]: value for key, value in vars(self).items()} | kwargs))

    def __str__(self) -> str:
        return str(vars(self))

__all__ = [
    'RoleRequest',
]

