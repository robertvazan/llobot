from __future__ import annotations
from datetime import datetime
from pathlib import Path
from typing import Iterable
from llobot.chats.archives import ChatArchive, standard_chat_archive
from llobot.chats.branches import ChatBranch
from llobot.chats.intents import ChatIntent
from llobot.commands.approve import ApproveCommand
from llobot.commands.chain import StepChain
from llobot.commands.custom import CustomStep
from llobot.commands.cutoff import CutoffCommand, ImplicitCutoffStep
from llobot.commands.project import ProjectCommand
from llobot.commands.unrecognized import UnrecognizedCommand
from llobot.crammers.example import ExampleCrammer, standard_example_crammer
from llobot.environments import Environment
from llobot.environments.commands import CommandsEnv
from llobot.environments.context import ContextEnv
from llobot.environments.cutoff import CutoffEnv
from llobot.environments.projects import ProjectEnv
from llobot.environments.prompt import PromptEnv
from llobot.environments.session import SessionEnv
from llobot.environments.status import StatusEnv
from llobot.formats.mentions import parse_mentions
from llobot.formats.prompts import PromptFormat, standard_prompt_format
from llobot.formats.prompts.reminder import ReminderPromptFormat
from llobot.utils.fs import data_home
from llobot.utils.zones import Zoning
from llobot.memories.examples import ExampleMemory
from llobot.models import Model
from llobot.models.streams import ModelStream
from llobot.projects import Project
from llobot.projects.library import ProjectLibrary, ProjectLibraryPrecursor, coerce_project_library
from llobot.prompts import Prompt
from llobot.roles import Role

class Imitator(Role):
    """
    A role that learns to perform tasks by imitating few-shot examples.

    The Imitator role is designed for tasks where behavior is defined by a
    collection of examples rather than a detailed system prompt with instructions.
    It stuffs the context with user-approved prompt/response pairs from previous
    conversations, leveraging the model's in-context learning capabilities. This
    is useful for simple, repetitive tasks like data transformation or style
    imitation. It supports an `@approve` command to save successful interactions
    as new examples.
    """
    _name: str
    _model: Model
    _system: str
    _crammer: ExampleCrammer
    _prompt_format: PromptFormat
    _reminder_format: PromptFormat
    _project_library: ProjectLibrary
    _step_chain: StepChain
    _examples: ExampleMemory

    def __init__(self, name: str, model: Model, *,
        prompt: str | Prompt = '',
        projects: ProjectLibraryPrecursor = (),
        example_archive: ChatArchive | Zoning | Path | str = standard_chat_archive(data_home()/'llobot/examples'),
        crammer: ExampleCrammer = standard_example_crammer(),
        prompt_format: PromptFormat = standard_prompt_format(),
        reminder_format: PromptFormat = ReminderPromptFormat(),
    ):
        self._name = name
        self._model = model
        self._examples = ExampleMemory(name, archive=example_archive)
        self._system = str(prompt)
        self._crammer = crammer
        self._prompt_format = prompt_format
        self._reminder_format = reminder_format
        self._project_library = coerce_project_library(projects)
        self._step_chain = StepChain(
            ProjectCommand(),
            CutoffCommand(),
            ImplicitCutoffStep(),
            CustomStep(self.stuff),
            ApproveCommand(self._examples),
            UnrecognizedCommand(),
        )

    @property
    def name(self) -> str:
        return self._name

    def stuff(self, env: Environment):
        """
        Populates the context with system prompt, examples, and reminders.

        Args:
            env: The environment to populate.
        """
        context_env = env[ContextEnv]
        if context_env.populated:
            return

        builder = context_env.builder
        builder.budget = self._model.context_budget

        builder.add(self._prompt_format.render_chat(self._system))

        recent_examples = self._examples.recent(env)
        self._crammer.cram(builder, recent_examples)

        builder.add(self._reminder_format.render_chat(self._system))

    def chat(self, prompt: ChatBranch) -> ModelStream:
        env = Environment()
        env[ProjectEnv].configure(self._project_library)
        context_env = env[ContextEnv]
        queue = env[CommandsEnv]
        prompt_env = env[PromptEnv]
        status_env = env[StatusEnv]

        for i, message in enumerate(prompt):
            if i + 1 == len(prompt):
                prompt_env.mark_last()

            if message.intent == ChatIntent.PROMPT:
                prompt_env.set(message.content)
                if i + 1 < len(prompt) and prompt[i + 1].intent == ChatIntent.SESSION:
                    queue.add(parse_mentions(prompt[i + 1]))
                queue.add(parse_mentions(message))
                self._step_chain.process(env)

            context_env.add(message)

        if status_env.populated:
            yield from status_env.stream()
            return

        session_env = env[SessionEnv]
        yield from session_env.stream()
        context_env.add(session_env.message())

        assembled_prompt = context_env.build()
        yield from self._model.generate(assembled_prompt)

__all__ = [
    'Imitator',
]
