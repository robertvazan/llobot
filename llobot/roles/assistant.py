from __future__ import annotations
from datetime import datetime
from llobot.chats.branches import ChatBranch
from llobot.chats.builders import ChatBuilder
from llobot.commands.chains import CommandChain
from llobot.commands.cutoffs import CutoffCommand
from llobot.commands.projects import ProjectCommand
from llobot.crammers.examples import ExampleCrammer, standard_example_crammer
from llobot.environments import Environment
from llobot.environments.cutoffs import CutoffEnv
from llobot.environments.projects import ProjectEnv
from llobot.environments.session_messages import SessionMessageEnv
from llobot.formats.prompts import (
    PromptFormat,
    reminder_prompt_format,
    standard_prompt_format,
)
from llobot.models import Model
from llobot.models.streams import ModelStream
from llobot.projects import Project
from llobot.prompts import Prompt
from llobot.roles import Role

class Assistant(Role):
    _system: str
    _crammer: ExampleCrammer
    _prompt_format: PromptFormat
    _reminder_format: PromptFormat
    _command_chain: CommandChain

    def __init__(self, name: str, model: Model, *,
        prompt: str | Prompt = '',
        projects: list[Project] | None = None,
        crammer: ExampleCrammer = standard_example_crammer(),
        prompt_format: PromptFormat = standard_prompt_format(),
        reminder_format: PromptFormat = reminder_prompt_format(),
        **kwargs,
    ):
        super().__init__(name, model, **kwargs)
        self._system = str(prompt)
        self._crammer = crammer
        self._prompt_format = prompt_format
        self._reminder_format = reminder_format
        self._command_chain = CommandChain(ProjectCommand(projects), CutoffCommand())

    def chat(self, prompt: ChatBranch) -> ModelStream:
        env = Environment()
        self._command_chain.handle_chat(prompt, env)
        project = env[ProjectEnv].get()
        cutoff = env[CutoffEnv].get()

        budget = self.model.context_budget
        builder = ChatBuilder()

        system_chat = self._prompt_format(self._system)
        builder.add(system_chat)
        budget -= system_chat.cost

        reminder_chat = self._reminder_format(self._system)
        budget -= reminder_chat.cost

        recent_examples = self.recent_examples(project, cutoff)
        examples = self._crammer(recent_examples, budget)
        builder.add(examples)

        # Add reminder at the end
        builder.add(reminder_chat)

        context = builder.build()
        assembled_prompt = context + prompt
        yield from env[SessionMessageEnv].stream()
        yield from self.model.generate(assembled_prompt)

    def handle_ok(self, chat: ChatBranch, cutoff: datetime):
        env = Environment()
        self._command_chain.handle_chat(chat, env)
        project = env[ProjectEnv].get()
        self.save_example(chat, project)

__all__ = [
    'Assistant',
]
