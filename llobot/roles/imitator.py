from __future__ import annotations
from typing import Iterable
from llobot.chats.branches import ChatBranch
from llobot.chats.intents import ChatIntent
from llobot.commands.chain import StepChain
from llobot.commands.custom import CustomStep
from llobot.commands.cutoff import CutoffCommand, ImplicitCutoffStep
from llobot.commands.project import ProjectCommand
from llobot.commands.unrecognized import UnrecognizedCommand
from llobot.crammers.examples import ExampleCrammer, standard_example_crammer
from llobot.environments import Environment
from llobot.environments.commands import CommandsEnv
from llobot.environments.context import ContextEnv
from llobot.environments.cutoff import CutoffEnv
from llobot.environments.projects import ProjectEnv
from llobot.environments.replay import ReplayEnv
from llobot.environments.session import SessionEnv
from llobot.formats.mentions import parse_mentions
from llobot.formats.prompts import (
    PromptFormat,
    reminder_prompt_format,
    standard_prompt_format,
)
from llobot.models import Model
from llobot.models.streams import ModelStream
from llobot.projects import Project
from llobot.projects.dummy import DummyProject
from llobot.prompts import Prompt
from llobot.roles import Role

class Imitator(Role):
    _system: str
    _crammer: ExampleCrammer
    _prompt_format: PromptFormat
    _reminder_format: PromptFormat
    _step_chain: StepChain

    def __init__(self, name: str, model: Model, *,
        prompt: str | Prompt = '',
        projects: Iterable[str | Project] = (),
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
        project_list = [DummyProject(p.name if isinstance(p, Project) else p) for p in projects]
        self._step_chain = StepChain(
            ProjectCommand(project_list),
            CutoffCommand(),
            ImplicitCutoffStep(),
            CustomStep(self.stuff),
            UnrecognizedCommand(),
        )

    def stuff(self, env: Environment):
        """
        Populates the context with system prompt, examples, and reminders.

        Args:
            env: The environment to populate.
        """
        context = env[ContextEnv]
        if context.messages:
            return

        project = env[ProjectEnv].get()
        cutoff = env[CutoffEnv].get()
        budget = self.model.context_budget

        system_chat = self._prompt_format(self._system)
        context.add(system_chat)
        budget -= system_chat.cost

        reminder_chat = self._reminder_format(self._system)
        budget -= reminder_chat.cost

        recent_examples = self.recent_examples(project, cutoff)
        examples = self._crammer(recent_examples, budget)
        context.add(examples)

        context.add(reminder_chat)

    def chat(self, prompt: ChatBranch) -> ModelStream:
        env = Environment()
        context = env[ContextEnv]
        queue = env[CommandsEnv]

        for i, message in enumerate(prompt):
            if i + 1 == len(prompt):
                env[ReplayEnv].start_recording()

            if message.intent == ChatIntent.PROMPT:
                if i + 1 < len(prompt) and prompt[i + 1].intent == ChatIntent.SESSION:
                    queue.add(parse_mentions(prompt[i + 1]))
                queue.add(parse_mentions(message))
                self._step_chain.process(env)

            context.add(message)

        session_env = env[SessionEnv]
        yield from session_env.stream()
        context.add(session_env.message())

        assembled_prompt = context.build()
        yield from self.model.generate(assembled_prompt)

    # def handle_ok(self, chat: ChatBranch, cutoff: datetime):
    #     env = Environment()
    #     self._step_chain.process_chat(chat, env)
    #     project = env[ProjectEnv].get()
    #     self.save_example(chat, project)

__all__ = [
    'Imitator',
]
