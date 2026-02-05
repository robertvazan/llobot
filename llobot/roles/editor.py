from __future__ import annotations
from functools import cache
from typing import Iterable
from llobot.commands.project import handle_project_commands
from llobot.commands.retrievals import handle_retrieval_commands
from llobot.crammers.knowledge import KnowledgeCrammer, standard_knowledge_crammer
from llobot.crammers.tree import TreeCrammer, standard_tree_crammer
from llobot.environments import Environment
from llobot.models import Model
from llobot.prompts import (
    Prompt,
    SystemPrompt,
    asking_prompt_section,
    answering_prompt_section,
    closing_prompt_section,
    overviews_prompt_section,
    read_prompt,
    tools_prompt_section,
)
from llobot.roles.agent import Agent
from llobot.tools import Tool, standard_tools

@cache
def editor_system_prompt() -> SystemPrompt:
    """
    Returns the standard system prompt for the editor role.
    """
    return SystemPrompt(
        read_prompt('editor.md'),
        tools_prompt_section(),
        asking_prompt_section(),
        answering_prompt_section(),
        overviews_prompt_section(),
        closing_prompt_section(),
    )

class Editor(Agent):
    """
    A role specialized for analyzing and editing files in a project.

    The Editor role is designed to handle software development tasks that involve
    reading and modifying source code. It assembles a context for the LLM that
    includes a system prompt, relevant files from a knowledge base, and a file
    tree. It supports commands for project selection (`@project`), file
    retrieval (`@path/to/file`), and uses session IDs to persist state.
    """
    _knowledge_crammer: KnowledgeCrammer
    _tree_crammer: TreeCrammer

    def __init__(self, name: str, model: Model, *,
        prompt: str | Prompt = editor_system_prompt(),
        tools: Iterable[Tool] = standard_tools(),
        knowledge_crammer: KnowledgeCrammer = standard_knowledge_crammer(),
        tree_crammer: TreeCrammer = standard_tree_crammer(),
        **kwargs,
    ):
        """
        Creates a new editor role.

        Args:
            name: The name of the role.
            model: The language model to use.
            prompt: The system prompt. Defaults to `editor_system_prompt()`.
            tools: An iterable of tools available to the agent.
            knowledge_crammer: Crammer for knowledge documents.
            tree_crammer: Crammer for the file tree.
            **kwargs: Additional arguments for the base `Agent` class.
        """
        super().__init__(name, model, prompt=prompt, tools=tools, **kwargs)
        self._knowledge_crammer = knowledge_crammer
        self._tree_crammer = tree_crammer

    def handle_setup(self, env: Environment):
        """
        Handles project commands.

        Args:
            env: The environment to prepare.
        """
        super().handle_setup(env)
        handle_project_commands(env)

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
        Populates the context with system prompt, knowledge, and tree.

        Args:
            env: The environment to populate.
        """
        super().stuff(env)
        self._tree_crammer.cram(env)
        self._knowledge_crammer.cram(env)

__all__ = [
    'editor_system_prompt',
    'Editor',
]
