from __future__ import annotations
from datetime import datetime
from llobot.projects import Project
from llobot.contexts import Context
from llobot.chats import ChatBranch
from llobot.models.caches import PromptCache
from llobot.experts.memory import ExpertMemory
import llobot.contexts

class ExpertRequest:
    _memory: ExpertMemory
    _prompt: ChatBranch
    _project: Project | None
    _cutoff: datetime
    _budget: int
    _context: Context
    _cache: PromptCache

    def __init__(self, *,
        memory: ExpertMemory,
        prompt: ChatBranch,
        project: Project | None = None,
        cutoff: datetime,
        budget: int,
        context: Context = llobot.contexts.empty(),
        cache: PromptCache = PromptCache(),
    ):
        self._memory = memory
        self._prompt = prompt
        self._project = project
        self._cutoff = cutoff
        self._budget = budget
        self._context = context
        self._cache = cache

    @property
    def memory(self) -> ExpertMemory:
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

    @property
    def context(self) -> Context:
        return self._context

    @property
    def cache(self) -> PromptCache:
        return self._cache

    def replace(self, **kwargs) -> ExpertRequest:
        return ExpertRequest(**({key[1:]: value for key, value in vars(self).items()} | kwargs))

    def __str__(self) -> str:
        return str(vars(self))

__all__ = [
    'ExpertRequest',
]

