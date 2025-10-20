from __future__ import annotations
from pathlib import Path
from llobot.chats.history import ChatHistory, standard_chat_history
from llobot.commands.approve import handle_approve_commands
from llobot.commands.project import handle_project_commands
from llobot.crammers.example import ExampleCrammer, standard_example_crammer
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.utils.fs import data_home
from llobot.utils.zones import Zoning
from llobot.memories.examples import ExampleMemory
from llobot.models import Model
from llobot.prompts import Prompt
from llobot.roles.agent import Agent

class Imitator(Agent):
    """
    A role that learns to perform tasks by imitating few-shot examples.

    The Imitator role is designed for tasks where behavior is defined by a
    collection of examples rather than a detailed system prompt with instructions.
    It stuffs the context with user-approved prompt/response pairs from previous
    conversations, leveraging the model's in-context learning capabilities. This
    is useful for simple, repetitive tasks like data transformation or style
    imitation. It supports an `@approve` command to save successful interactions
    as new examples. Its examples can be scoped to a project.
    """
    _crammer: ExampleCrammer
    _examples: ExampleMemory

    def __init__(self, name: str, model: Model, *,
        prompt: str | Prompt = '',
        example_history: ChatHistory | Zoning | Path | str = standard_chat_history(data_home()/'llobot/examples'),
        crammer: ExampleCrammer = standard_example_crammer(),
        **kwargs,
    ):
        """
        Creates a new imitator role.

        Args:
            name: The name of the role.
            model: The language model to use.
            prompt: The system prompt. Defaults to empty.
            example_history: Storage for approved examples.
            crammer: Crammer for few-shot examples.
            **kwargs: Additional arguments for the base `Agent` class.
        """
        super().__init__(name, model, prompt=prompt, **kwargs)
        self._examples = ExampleMemory(name, history=example_history)
        self._crammer = crammer

    def handle_setup(self, env: Environment):
        """
        Handles project commands before stuffing the context.

        Args:
            env: The environment to prepare.
        """
        super().handle_setup(env)
        handle_project_commands(env)

    def handle_commands(self, env: Environment):
        """
        Handles the @approve command.

        Args:
            env: The environment.
        """
        super().handle_commands(env)
        handle_approve_commands(env, self._examples)

    def stuff(self, env: Environment):
        """
        Populates the context with system prompt, examples, and reminders.

        Args:
            env: The environment to populate.
        """
        super().stuff(env)
        builder = env[ContextEnv].builder
        recent_examples = self._examples.recent(env)
        self._crammer.cram(builder, recent_examples)
        builder.add(self._reminder_format.render_chat(self._system))

__all__ = [
    'Imitator',
]
