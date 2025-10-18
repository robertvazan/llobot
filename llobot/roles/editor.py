from __future__ import annotations
from functools import cache
from pathlib import Path
from llobot.chats.branches import ChatBranch
from llobot.chats.intents import ChatIntent
from llobot.commands import Step
from llobot.commands.chain import StepChain
from llobot.commands.custom import CustomStep
from llobot.commands.cutoff import CutoffCommand, ImplicitCutoffStep
from llobot.commands.knowledge import ProjectKnowledgeStep
from llobot.commands.project import ProjectCommand
from llobot.commands.retrievals import standard_retrieval_step
from llobot.commands.unrecognized import UnrecognizedCommand
from llobot.crammers.index import IndexCrammer, standard_index_crammer
from llobot.crammers.knowledge import KnowledgeCrammer, standard_knowledge_crammer
from llobot.environments import Environment
from llobot.environments.commands import CommandsEnv
from llobot.environments.context import ContextEnv
from llobot.environments.cutoff import CutoffEnv
from llobot.environments.knowledge import KnowledgeEnv
from llobot.environments.projects import ProjectEnv
from llobot.environments.prompt import PromptEnv
from llobot.environments.session import SessionEnv
from llobot.environments.status import StatusEnv
from llobot.formats.mentions import parse_mentions
from llobot.formats.prompts import PromptFormat, standard_prompt_format
from llobot.formats.prompts.reminder import ReminderPromptFormat
from llobot.knowledge.archives import KnowledgeArchive, standard_knowledge_archive
from llobot.models import Model
from llobot.models.streams import ModelStream
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
    retrieval (`@path/to/file`), and setting a knowledge cutoff time (`@cutoff`).
    """
    _name: str
    _model: Model
    _system: str
    _knowledge_archive: KnowledgeArchive
    _knowledge_crammer: KnowledgeCrammer
    _index_crammer: IndexCrammer
    _prompt_format: PromptFormat
    _reminder_format: PromptFormat
    _project_library: ProjectLibrary
    _step_chain: StepChain

    def __init__(self, name: str, model: Model, *,
        prompt: str | Prompt = editor_system_prompt(),
        projects: ProjectLibraryPrecursor = (),
        knowledge_archive: KnowledgeArchive = standard_knowledge_archive(),
        knowledge_crammer: KnowledgeCrammer = standard_knowledge_crammer(),
        index_crammer: IndexCrammer = standard_index_crammer(),
        prompt_format: PromptFormat = standard_prompt_format(),
        reminder_format: PromptFormat = ReminderPromptFormat(),
        retrieval_step: Step = standard_retrieval_step(),
    ):
        """
        Creates a new editor role.
        """
        self._name = name
        self._model = model
        self._system = str(prompt)
        self._knowledge_archive = knowledge_archive
        self._knowledge_crammer = knowledge_crammer
        self._index_crammer = index_crammer
        self._prompt_format = prompt_format
        self._reminder_format = reminder_format
        self._project_library = coerce_project_library(projects)
        self._step_chain = StepChain(
            ProjectCommand(),
            CutoffCommand(),
            ImplicitCutoffStep(self._knowledge_archive),
            ProjectKnowledgeStep(self._knowledge_archive),
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
                env[CutoffEnv].clear()
                prompt_env.set(message.content)
                if i + 1 < len(prompt) and prompt[i + 1].intent == ChatIntent.SESSION:
                    queue.add(parse_mentions(prompt[i + 1]))
                queue.add(parse_mentions(message))
                self._step_chain.process(env)

            if i == 0:
                context_env.add(self._reminder_format.render_chat(self._system))

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
    'editor_system_prompt',
    'Editor',
]
