from __future__ import annotations
from functools import cache
from pathlib import Path
from llobot.chats.thread import ChatThread
from llobot.chats.intent import ChatIntent
from llobot.commands.knowledge import populate_knowledge_env
from llobot.commands.project import handle_project_commands
from llobot.commands.retrievals import handle_retrieval_commands
from llobot.commands.session import ensure_session_command, handle_session_commands
from llobot.commands.unrecognized import handle_unrecognized_commands
from llobot.crammers.index import IndexCrammer, standard_index_crammer
from llobot.crammers.knowledge import KnowledgeCrammer, standard_knowledge_crammer
from llobot.environments import Environment
from llobot.environments.commands import CommandsEnv
from llobot.environments.context import ContextEnv
from llobot.environments.history import SessionHistory, coerce_session_history, standard_session_history
from llobot.environments.knowledge import KnowledgeEnv
from llobot.environments.projects import ProjectEnv
from llobot.environments.prompt import PromptEnv
from llobot.environments.session import SessionEnv
from llobot.environments.status import StatusEnv
from llobot.formats.mentions import parse_mentions
from llobot.formats.prompts import PromptFormat, standard_prompt_format
from llobot.formats.prompts.reminder import ReminderPromptFormat
from llobot.models import Model
from llobot.chats.stream import ChatStream
from llobot.projects.library import ProjectLibrary, ProjectLibraryPrecursor, coerce_project_library
from llobot.prompts import (
    Prompt,
    SystemPrompt,
    answering_prompt_section,
    editing_prompt_section,
    overviews_prompt_section,
    read_prompt,
)
from llobot.roles import Role
from llobot.utils.zones import Zoning

@cache
def editor_system_prompt() -> SystemPrompt:
    """
    Returns the standard system prompt for the editor role.
    """
    return SystemPrompt(
        read_prompt('editor.md'),
        editing_prompt_section(),
        answering_prompt_section(),
        overviews_prompt_section(),
    )

class Editor(Role):
    """
    A role specialized for analyzing and editing files in a project.

    The Editor role is designed to handle software development tasks that involve
    reading and modifying source code. It assembles a context for the LLM that
    includes a system prompt, relevant files from a knowledge base, and a file
    index. It supports commands for project selection (`@project`), file
    retrieval (`@path/to/file`), and uses session IDs to persist state.
    """
    _name: str
    _model: Model
    _system: str
    _session_history: SessionHistory
    _knowledge_crammer: KnowledgeCrammer
    _index_crammer: IndexCrammer
    _prompt_format: PromptFormat
    _reminder_format: PromptFormat
    _project_library: ProjectLibrary

    def __init__(self, name: str, model: Model, *,
        prompt: str | Prompt = editor_system_prompt(),
        projects: ProjectLibraryPrecursor = (),
        session_history: SessionHistory | Zoning | Path | str = standard_session_history(),
        knowledge_crammer: KnowledgeCrammer = standard_knowledge_crammer(),
        index_crammer: IndexCrammer = standard_index_crammer(),
        prompt_format: PromptFormat = standard_prompt_format(),
        reminder_format: PromptFormat = ReminderPromptFormat(),
    ):
        """
        Creates a new editor role.

        Args:
            name: The name of the role.
            model: The language model to use.
            prompt: The system prompt. Defaults to `editor_system_prompt()`.
            projects: A project library or a precursor for one.
            session_history: Session history storage. Defaults to the standard one.
            knowledge_crammer: Crammer for knowledge documents.
            index_crammer: Crammer for the file index.
            prompt_format: Format for the main system prompt.
            reminder_format: Format for reminder prompts.
        """
        self._name = name
        self._model = model
        self._system = str(prompt)
        self._session_history = coerce_session_history(session_history)
        self._knowledge_crammer = knowledge_crammer
        self._index_crammer = index_crammer
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
        populate_knowledge_env(env)
        self.stuff(env)
        self._handle_retrievals(env)
        self._handle_extra_commands(env)
        handle_unrecognized_commands(env)

    def _handle_retrievals(self, env: Environment):
        """
        Handles retrieval commands. Can be overridden.

        Args:
            env: The environment.
        """
        handle_retrieval_commands(env)

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
        Populates the context with system prompt, knowledge, and index.

        Args:
            env: The environment to populate.
        """
        if env[ContextEnv].populated:
            return

        builder = env[ContextEnv].builder
        builder.budget = self._model.context_budget
        knowledge = env[KnowledgeEnv].get()

        # System prompt (unconditionally included)
        builder.add(self._prompt_format.render_chat(self._system))

        # Index
        self._index_crammer.cram(builder, knowledge)

        # Knowledge
        self._knowledge_crammer.cram(builder, knowledge)

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
    'editor_system_prompt',
    'Editor',
]
