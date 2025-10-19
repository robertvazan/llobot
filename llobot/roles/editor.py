from __future__ import annotations
from functools import cache
from pathlib import Path
from llobot.chats.thread import ChatThread
from llobot.chats.intent import ChatIntent
from llobot.commands import Step
from llobot.commands.chain import StepChain
from llobot.commands.custom import CustomStep
from llobot.commands.knowledge import ProjectKnowledgeStep
from llobot.commands.project import ProjectCommand
from llobot.commands.retrievals import standard_retrieval_step
from llobot.commands.session import ImplicitSessionStep, SessionCommand, SessionLoadStep
from llobot.commands.unrecognized import UnrecognizedCommand
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
    _step_chain: StepChain

    def __init__(self, name: str, model: Model, *,
        prompt: str | Prompt = editor_system_prompt(),
        projects: ProjectLibraryPrecursor = (),
        session_history: SessionHistory | Zoning | Path | str = standard_session_history(),
        knowledge_crammer: KnowledgeCrammer = standard_knowledge_crammer(),
        index_crammer: IndexCrammer = standard_index_crammer(),
        prompt_format: PromptFormat = standard_prompt_format(),
        reminder_format: PromptFormat = ReminderPromptFormat(),
        retrieval_step: Step = standard_retrieval_step(),
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
            retrieval_step: Step for handling document retrieval commands.
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
        self._step_chain = StepChain(
            ImplicitSessionStep(),
            SessionLoadStep(self._session_history),
            ProjectCommand(),
            ProjectKnowledgeStep(),
            CustomStep(self.stuff),
            retrieval_step,
            UnrecognizedCommand(),
        )

    @property
    def name(self) -> str:
        return self._name

    def stuff(self, env: Environment):
        """
        Populates the context with system prompt, knowledge, and index.

        Args:
            env: The environment to populate.
        """
        context_env = env[ContextEnv]
        if context_env.populated:
            return

        knowledge = env[KnowledgeEnv].get()
        builder = context_env.builder
        builder.budget = self._model.context_budget

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
    'editor_system_prompt',
    'Editor',
]
