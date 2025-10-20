from __future__ import annotations
from functools import cache
from llobot.commands.knowledge import populate_knowledge_env
from llobot.commands.project import handle_project_commands
from llobot.commands.retrievals import handle_retrieval_commands
from llobot.crammers.index import IndexCrammer, standard_index_crammer
from llobot.crammers.knowledge import KnowledgeCrammer, standard_knowledge_crammer
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.knowledge import KnowledgeEnv
from llobot.models import Model
from llobot.prompts import (
    Prompt,
    SystemPrompt,
    answering_prompt_section,
    editing_prompt_section,
    overviews_prompt_section,
    read_prompt,
)
from llobot.roles.agent import Agent

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

class Editor(Agent):
    """
    A role specialized for analyzing and editing files in a project.

    The Editor role is designed to handle software development tasks that involve
    reading and modifying source code. It assembles a context for the LLM that
    includes a system prompt, relevant files from a knowledge base, and a file
    index. It supports commands for project selection (`@project`), file
    retrieval (`@path/to/file`), and uses session IDs to persist state.
    """
    _knowledge_crammer: KnowledgeCrammer
    _index_crammer: IndexCrammer

    def __init__(self, name: str, model: Model, *,
        prompt: str | Prompt = editor_system_prompt(),
        knowledge_crammer: KnowledgeCrammer = standard_knowledge_crammer(),
        index_crammer: IndexCrammer = standard_index_crammer(),
        **kwargs,
    ):
        """
        Creates a new editor role.

        Args:
            name: The name of the role.
            model: The language model to use.
            prompt: The system prompt. Defaults to `editor_system_prompt()`.
            knowledge_crammer: Crammer for knowledge documents.
            index_crammer: Crammer for the file index.
            **kwargs: Additional arguments for the base `Agent` class.
        """
        super().__init__(name, model, prompt=prompt, **kwargs)
        self._knowledge_crammer = knowledge_crammer
        self._index_crammer = index_crammer

    def handle_setup(self, env: Environment):
        """
        Handles project commands and populates the knowledge environment.

        Args:
            env: The environment to prepare.
        """
        super().handle_setup(env)
        handle_project_commands(env)
        populate_knowledge_env(env)

    def handle_commands(self, env: Environment):
        """
        Handles retrieval commands.

        Args:
            env: The environment.
        """
        super().handle_commands(env)
        handle_retrieval_commands(env)

    def stuff(self, env: Environment):
        """
        Populates the context with system prompt, knowledge, and index.

        Args:
            env: The environment to populate.
        """
        super().stuff(env)
        builder = env[ContextEnv].builder
        knowledge = env[KnowledgeEnv].get()
        self._index_crammer.cram(builder, knowledge)
        self._knowledge_crammer.cram(builder, knowledge)

__all__ = [
    'editor_system_prompt',
    'Editor',
]
