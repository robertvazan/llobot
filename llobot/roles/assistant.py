from __future__ import annotations
from llobot.crammers.examples import ExampleCrammer
from llobot.formatters.prompts import PromptFormatter
from llobot.prompts import Prompt
from llobot.roles import Role
from llobot.chats import ChatBranch, ChatBuilder
from llobot.projects import Project
from llobot.models import Model
import llobot.crammers.examples
import llobot.formatters.prompts

class Assistant(Role):
    _prompt: str
    _crammer: ExampleCrammer
    _prompt_formatter: PromptFormatter
    _reminder_formatter: PromptFormatter

    def __init__(self, name: str, model: Model, *,
        prompt: str | Prompt = '',
        crammer: ExampleCrammer = llobot.crammers.examples.standard(),
        prompt_formatter: PromptFormatter = llobot.formatters.prompts.standard(),
        reminder_formatter: PromptFormatter = llobot.formatters.prompts.reminder(),
        **kwargs,
    ):
        super().__init__(name, model, **kwargs)
        self._prompt = str(prompt)
        self._crammer = crammer
        self._prompt_formatter = prompt_formatter
        self._reminder_formatter = reminder_formatter

    def stuff(self, *,
        prompt: ChatBranch,
    ) -> ChatBranch:
        project = self.resolve_project(prompt)
        budget = self.model.context_budget
        chat = ChatBuilder()

        system_chat = self._prompt_formatter(self._prompt)
        chat.add(system_chat)
        budget -= system_chat.cost

        reminder_chat = self._reminder_formatter(self._prompt)
        budget -= reminder_chat.cost

        recent_examples = self.recent_examples(project)
        examples = self._crammer(recent_examples, budget)
        chat.add(examples)

        # Add reminder at the end
        chat.add(reminder_chat)

        return chat.build()

__all__ = [
    'Assistant',
]
