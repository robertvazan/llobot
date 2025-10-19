from __future__ import annotations
from datetime import datetime
from pathlib import Path
from typing import Iterable
from llobot.chats.history import ChatHistory, standard_chat_history
from llobot.chats.thread import ChatThread
from llobot.chats.intent import ChatIntent
from llobot.commands.approve import handle_approve_commands
from llobot.commands.project import handle_project_commands
from llobot.commands.session import ensure_session_command, handle_session_commands
from llobot.commands.unrecognized import handle_unrecognized_commands
from llobot.crammers.example import ExampleCrammer, standard_example_crammer
from llobot.environments import Environment
from llobot.environments.commands import CommandsEnv
from llobot.environments.context import ContextEnv
from llobot.environments.history import SessionHistory, coerce_session_history, standard_session_history
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
    _examples: ExampleMemory
    _session_history: SessionHistory

    def __init__(self, name: str, model: Model, *,
        prompt: str | Prompt = '',
        projects: ProjectLibraryPrecursor = (),
        session_history: SessionHistory | Zoning | Path | str = standard_session_history(),
        example_history: ChatHistory | Zoning | Path | str = standard_chat_history(data_home()/'llobot/examples'),
        crammer: ExampleCrammer = standard_example_crammer(),
        prompt_format: PromptFormat = standard_prompt_format(),
        reminder_format: PromptFormat = ReminderPromptFormat(),
    ):
        """
        Creates a new imitator role.

        Args:
            name: The name of the role.
            model: The language model to use.
            prompt: The system prompt. Defaults to empty.
            projects: A project library or a precursor for one.
            session_history: Session history storage. Defaults to the standard one.
            example_history: Storage for approved examples.
            crammer: Crammer for few-shot examples.
            prompt_format: Format for the main system prompt.
            reminder_format: Format for reminder prompts.
        """
        self._name = name
        self._model = model
        self._session_history = coerce_session_history(session_history)
        self._examples = ExampleMemory(name, history=example_history)
        self._system = str(prompt)
        self._crammer = crammer
        self._prompt_format = prompt_format
        self._reminder_format = reminder_format
        self._project_library = coerce_project_library(projects)

    @property
    def name(self) -> str:
        return self._name

    def _process_commands(self, env: Environment):
        """
        Processes commands and populates the environment.
        This method can be overridden by subclasses to customize command handling.

        Args:
            env: The environment to process commands in.
        """
        ensure_session_command(env)
        session_id = env[SessionEnv].get_id()
        if session_id:
            self._session_history.load(session_id, env)
        handle_project_commands(env)
        self.stuff(env)
        handle_approve_commands(env, self._examples)
        self._handle_extra_commands(env)
        handle_unrecognized_commands(env)

    def _handle_extra_commands(self, env: Environment):
        """
        Hook for subclasses to add custom command handlers. Runs before the
        unrecognized command handler.

        Args:
            env: The environment.
        """
        pass

    def stuff(self, env: Environment):
        """
        Populates the context with system prompt, examples, and reminders.

        Args:
            env: The environment to populate.
        """
        if env[ContextEnv].populated:
            return

        builder = env[ContextEnv].builder
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

        for m in prompt:
            if m.intent == ChatIntent.SESSION:
                env[CommandsEnv].add(parse_mentions(m))
        handle_session_commands(env)
        handle_unrecognized_commands(env)

        env[PromptEnv].set(prompt[-1].content)
        env[CommandsEnv].add(parse_mentions(prompt[-1]))
        self._process_commands(env)

        context_env = env[ContextEnv]
        if len(prompt) == 1:
            context_env.add(self._reminder_format.render_chat(self._system))
        context_env.add(prompt[-1])

        yield from context_env.record(env[SessionEnv].stream())
        if env[StatusEnv].populated:
            yield from context_env.record(env[StatusEnv].stream())
        else:
            assembled_prompt = context_env.build()
            model_stream = self._model.generate(assembled_prompt)
            yield from context_env.record(model_stream)

        session_id = env[SessionEnv].get_id()
        self._session_history.save(session_id, env)

__all__ = [
    'Imitator',
]
