from __future__ import annotations
from llobot.commands.chains import CommandChain
from llobot.commands.projects import ProjectCommand
from llobot.crammers.examples import ExampleCrammer
from llobot.environments import Environment
from llobot.environments.projects import ProjectEnv
from llobot.formatters.prompts import PromptFormatter
from llobot.prompts import Prompt
from llobot.roles import Role
from llobot.chats import ChatBranch, ChatBuilder
from llobot.projects import Project
from llobot.models import Model
from llobot.models.streams import ModelStream
import llobot.commands.mentions
import llobot.crammers.examples
import llobot.formatters.prompts
from datetime import datetime

class Assistant(Role):
    _system: str
    _crammer: ExampleCrammer
    _prompt_formatter: PromptFormatter
    _reminder_formatter: PromptFormatter
    _command_chain: CommandChain

    def __init__(self, name: str, model: Model, *,
        prompt: str | Prompt = '',
        projects: list[Project] | None = None,
        crammer: ExampleCrammer = llobot.crammers.examples.standard(),
        prompt_formatter: PromptFormatter = llobot.formatters.prompts.standard(),
        reminder_formatter: PromptFormatter = llobot.formatters.prompts.reminder(),
        **kwargs,
    ):
        super().__init__(name, model, **kwargs)
        self._system = str(prompt)
        self._crammer = crammer
        self._prompt_formatter = prompt_formatter
        self._reminder_formatter = reminder_formatter
        self._command_chain = CommandChain(ProjectCommand(projects))

    def chat(self, prompt: ChatBranch) -> ModelStream:
        env = Environment()
        commands = llobot.commands.mentions.parse(prompt)
        self._command_chain(commands, env)
        project = env[ProjectEnv].get()

        budget = self.model.context_budget
        builder = ChatBuilder()

        system_chat = self._prompt_formatter(self._system)
        builder.add(system_chat)
        budget -= system_chat.cost

        reminder_chat = self._reminder_formatter(self._system)
        budget -= reminder_chat.cost

        recent_examples = self.recent_examples(project)
        examples = self._crammer(recent_examples, budget)
        builder.add(examples)

        # Add reminder at the end
        builder.add(reminder_chat)

        context = builder.build()
        assembled_prompt = context + prompt
        return self.model.generate(assembled_prompt)

    def handle_ok(self, chat: ChatBranch, cutoff: datetime):
        env = Environment()
        commands = llobot.commands.mentions.parse(chat)
        self._command_chain(commands, env)
        project = env[ProjectEnv].get()
        self.save_example(chat, project)

__all__ = [
    'Assistant',
]
