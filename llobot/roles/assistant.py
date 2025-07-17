from __future__ import annotations
from datetime import datetime
from llobot.crammers.examples import ExampleCrammer
from llobot.formatters.instructions import InstructionFormatter
from llobot.roles import Role
from llobot.chats import ChatBranch, ChatBuilder
from llobot.projects import Project
import llobot.crammers.examples
import llobot.formatters.instructions

class Assistant(Role):
    _instructions: str
    _crammer: ExampleCrammer
    _instruction_formatter: InstructionFormatter

    def __init__(self, name: str, *,
        instructions: str = '',
        crammer: ExampleCrammer = llobot.crammers.examples.standard(),
        instruction_formatter: InstructionFormatter = llobot.formatters.instructions.standard(),
        **kwargs,
    ):
        super().__init__(name, **kwargs)
        self._instructions = instructions
        self._crammer = crammer
        self._instruction_formatter = instruction_formatter

    def stuff(self, *,
        prompt: ChatBranch,
        project: Project | None,
        cutoff: datetime,
        budget: int,
    ) -> ChatBranch:
        chat = ChatBuilder()
        
        system_chat = self._instruction_formatter(self._instructions)
        chat.add(system_chat)
        budget -= system_chat.cost

        recent_examples = self.recent_examples(project, cutoff)
        examples = self._crammer(recent_examples, budget)
        chat.add(examples)
        
        return chat.build()

__all__ = [
    'Assistant',
]
