from __future__ import annotations
from datetime import datetime
from llobot.crammers.examples import ExampleCrammer
from llobot.formatters.prompts import PromptFormatter
from llobot.roles import Role
from llobot.chats import ChatBranch, ChatBuilder
from llobot.projects import Project
import llobot.crammers.examples
import llobot.formatters.prompts

class Assistant(Role):
    _prompt: str
    _crammer: ExampleCrammer
    _prompt_formatter: PromptFormatter

    def __init__(self, name: str, *,
        prompt: str = '',
        crammer: ExampleCrammer = llobot.crammers.examples.standard(),
        prompt_formatter: PromptFormatter = llobot.formatters.prompts.standard(),
        **kwargs,
    ):
        super().__init__(name, **kwargs)
        self._prompt = prompt
        self._crammer = crammer
        self._prompt_formatter = prompt_formatter

    def stuff(self, *,
        prompt: ChatBranch,
        project: Project | None,
        cutoff: datetime,
        budget: int,
    ) -> ChatBranch:
        chat = ChatBuilder()

        system_chat = self._prompt_formatter(self._prompt)
        chat.add(system_chat)
        budget -= system_chat.cost

        recent_examples = self.recent_examples(project, cutoff)
        examples = self._crammer(recent_examples, budget)
        chat.add(examples)

        return chat.build()

__all__ = [
    'Assistant',
]
