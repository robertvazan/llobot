from __future__ import annotations
from datetime import datetime
from pathlib import Path
from typing import Iterable
from llobot.chats.history import ChatHistory, standard_chat_history
from llobot.chats.thread import ChatThread
from llobot.chats.intent import ChatIntent
from llobot.commands.approve import ApproveCommand
from llobot.commands.chain import StepChain
from llobot.commands.custom import CustomStep
from llobot.commands.project import ProjectCommand
from llobot.commands.session import ImplicitSessionStep, SessionCommand, SessionLoadStep
from llobot.commands.unrecognized import UnrecognizedCommand
from llobot.crammers.example import ExampleCrammer, standard_example_crammer
from llobot.environments import Environment
from llobot.environments.commands import CommandsEnv
from llobot.environments.context import ContextEnv
from llobot.environments.history import SessionHistory, coerce_session_history
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
from llobot.chats.stream import ChatStream
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
    _session_history: SessionHistory

    def __init__(self, name: str, model: Model, *,
        prompt: str | Prompt = '',
        projects: ProjectLibraryPrecursor = (),
        session_history: SessionHistory | Zoning | Path | str,
        example_history: ChatHistory | Zoning | Path | str = standard_chat_history(data_home()/'llobot/examples'),
        crammer: ExampleCrammer = standard_example_crammer(),
        prompt_format: PromptFormat = standard_prompt_format(),
        reminder_format: PromptFormat = ReminderPromptFormat(),
    ):
        self._name = name
        self._model = model
        self._session_history = coerce_session_history(session_history)
        self._examples = ExampleMemory(name, history=example_history)
        self._system = str(prompt)
        self._crammer = crammer
        self._prompt_format = prompt_format
        self._reminder_format = reminder_format
        self._project_library = coerce_project_library(projects)
        self._step_chain = StepChain(
            ImplicitSessionStep(),
            SessionLoadStep(self._session_history),
            ProjectCommand(),
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

    def chat(self, prompt: ChatThread) -> ChatStream:
        if not prompt or prompt[-1].intent != ChatIntent.PROMPT:
            raise ValueError("The last message in the chat thread must be a PROMPT.")

        env = Environment()
        env[ProjectEnv].configure(self._project_library)

        session_messages = [m for m in prompt if m.intent == ChatIntent.SESSION]
        session_command_chain = StepChain(SessionCommand(), UnrecognizedCommand())
        queue = env[CommandsEnv]
        for m in session_messages:
            queue.add(parse_mentions(m))
        session_command_chain.process(env)

        last_prompt_message = prompt[-1]
        env[PromptEnv].set(last_prompt_message.content)
        env[CommandsEnv].add(parse_mentions(last_prompt_message))
        self._step_chain.process(env)

        context_env = env[ContextEnv]
        if len(prompt) == 1:
            context_env.add(self._reminder_format.render_chat(self._system))
        context_env.add(last_prompt_message)

        status_env = env[StatusEnv]
        if status_env.populated:
            yield from context_env.record(status_env.stream())
        else:
            session_env = env[SessionEnv]
            yield from context_env.record(session_env.stream())

            assembled_prompt = context_env.build()
            model_stream = self._model.generate(assembled_prompt)
            yield from context_env.record(model_stream)

        session_id = env[SessionEnv].get_id()
        self._session_history.save(session_id, env)

__all__ = [
    'Imitator',
]
