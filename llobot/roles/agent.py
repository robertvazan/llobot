from __future__ import annotations
from pathlib import Path
from typing import Iterable, Mapping
from llobot.chats.thread import ChatThread
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.stream import ChatStream
from llobot.commands.run import handle_run_commands
from llobot.commands.echo import handle_echo_commands
from llobot.commands.model import handle_model_commands
from llobot.commands.autonomy import handle_autonomy_commands
from llobot.commands.unrecognized import handle_unrecognized_commands
from llobot.environments import Environment
from llobot.environments.autonomy import AutonomyEnv
from llobot.environments.commands import CommandsEnv
from llobot.environments.context import ContextEnv
from llobot.environments.history import SessionHistory, coerce_session_history, standard_session_history
from llobot.environments.model import ModelEnv
from llobot.environments.projects import ProjectEnv
from llobot.environments.prompt import PromptEnv
from llobot.environments.tools import ToolEnv
from llobot.formats.mentions import parse_mentions
from llobot.formats.prompts import PromptFormat, standard_prompt_format
from llobot.formats.prompts.reminder import ReminderPromptFormat
from llobot.models import Model
from llobot.models.library import ModelLibrary
from llobot.models.library.empty import EmptyModelLibrary
from llobot.projects.library import ProjectLibrary
from llobot.projects.library.empty import EmptyProjectLibrary
from llobot.prompts import Prompt
from llobot.roles import Role
from llobot.roles.autonomy import Autonomy, LimitedAutonomy, NoAutonomy, StepAutonomy
from llobot.tools import Tool
from llobot.tools.execution import execute_tool_calls
from llobot.utils.text import quote_code
from llobot.utils.zones import Zoning

class Agent(Role):
    """
    A base role for agents that handle sessions, environment, and command execution.

    This class provides a framework for creating roles that interact with a user
    through a prompt thread. It manages session persistence, command parsing,
    and context assembly. Subclasses can customize behavior by overriding methods
    for context stuffing, command handling, and prompt generation.
    """
    _name: str
    _model: Model
    _system: str
    _session_history: SessionHistory
    _prompt_format: PromptFormat
    _reminder_format: PromptFormat
    _project_library: ProjectLibrary
    _model_library: ModelLibrary
    _tools: tuple[Tool, ...]
    _autonomy: Autonomy
    _autonomy_profiles: Mapping[str, Autonomy]

    def __init__(self, name: str, model: Model, *,
        prompt: str | Prompt = '',
        projects: ProjectLibrary | None = None,
        models: ModelLibrary | None = None,
        tools: Iterable[Tool] = (),
        autonomy: Autonomy | None = None,
        autonomy_profiles: Mapping[str, Autonomy] | None = None,
        session_history: SessionHistory | Zoning | Path | str = standard_session_history(),
        prompt_format: PromptFormat = standard_prompt_format(),
        reminder_format: PromptFormat = ReminderPromptFormat(),
    ):
        """
        Initializes the Agent role.

        Args:
            name: The name of the role.
            model: The default language model to use.
            prompt: The system prompt.
            projects: A project library or a precursor for one.
            models: A model library.
            tools: An iterable of tools available to the agent.
            autonomy: The autonomy level of the agent. Defaults to LimitedAutonomy.
            session_history: Session history storage.
            prompt_format: Format for the main system prompt.
            reminder_format: Format for reminder prompts.
        """
        self._name = name
        self._model = model
        self._system = str(prompt)
        self._project_library = projects or EmptyProjectLibrary()
        self._model_library = models or EmptyModelLibrary()
        self._tools = tuple(tools)
        self._autonomy = autonomy or LimitedAutonomy()
        if autonomy_profiles is not None:
            self._autonomy_profiles = autonomy_profiles
        else:
            self._autonomy_profiles = {
                'off': NoAutonomy(),
                'step': StepAutonomy(),
                'low': LimitedAutonomy(turns=5),
                'high': LimitedAutonomy(),
            }
        self._session_history = coerce_session_history(session_history)
        self._prompt_format = prompt_format
        self._reminder_format = reminder_format

    @property
    def name(self) -> str:
        return self._name

    def parse_prompt(self, env: Environment, prompt: ChatThread):
        """
        Parses the full prompt thread, loads session, and prepares environment.

        This method sets the full prompt thread (which also computes the session
        ID), loads the previous session from history, and extracts commands from
        the current (last) prompt message.

        Args:
            env: The environment to populate.
            prompt: The full prompt thread from the user's client.
        """
        prompt_env = env[PromptEnv]
        prompt_env.set(prompt)

        # Load session data for the previous session ID.
        self._session_history.load(env)

        # Add the current prompt eagerly so that it appears before any output
        # generated by setup or command handling (e.g. status messages).
        env[ContextEnv].add(prompt[-1])

        # Parse commands from the current prompt message.
        env[CommandsEnv].add(parse_mentions(prompt[-1]))

    def handle_prompt(self, env: Environment):
        """
        Processes commands and populates the environment.

        This method orchestrates command handling. It delegates setup to `handle_setup`.
        It performs context stuffing if this is the first turn of the conversation
        (or if the context is missing). Finally, it delegates command processing
        to `handle_commands`.

        Args:
            env: The environment to process commands in.
        """
        self.handle_setup(env)

        # Context stuffing is performed only at the beginning of the conversation.
        if env[PromptEnv].previous_hash is None:
            # The context currently contains the user prompt and any messages generated during setup.
            # We must preserve them while inserting system prompts (stuffing) at the beginning.
            preserved_messages = env[ContextEnv].build()
            env[ContextEnv].clear()

            self.stuff(env)
            self.remind(env)

            env[ContextEnv].add(preserved_messages)

        try:
            self.handle_commands(env)
            handle_unrecognized_commands(env)
        except Exception as e:
            env[ContextEnv].add(ChatMessage(ChatIntent.STATUS, f"Error processing commands: {quote_code(str(e))}"))
            env[PromptEnv].swallow()

    def handle_setup(self, env: Environment):
        """
        Hook for subclasses to prepare the environment before stuffing.

        This is called before the context is stuffed. It can be used to
        populate environment components that `stuff` depends on, such as
        selecting model, project, and loading a knowledge base.

        Args:
            env: The environment to prepare.
        """
        handle_model_commands(env)

    def stuff(self, env: Environment):
        """
        Populates the context with the system prompt and sets the budget.

        Subclasses should override this to add more content like knowledge
        documents or few-shot examples, but they should call `super().stuff(env)`
        to ensure the budget is set and the base system prompt is added.

        Args:
            env: The environment to populate.
        """
        builder = env[ContextEnv].builder
        builder.budget = env[ModelEnv].get().context_budget
        builder.add(self._prompt_format.render_chat(self._system))

    def remind(self, env: Environment):
        """
        Adds a reminder prompt to the context.

        This is typically used for the first turn to reinforce the system prompt.

        Args:
            env: The environment to add the reminder to.
        """
        env[ContextEnv].add(self._reminder_format.render_chat(self._system))

    def handle_commands(self, env: Environment):
        """
        Hook for subclasses to add custom command handlers.

        This method is called after stuffing and before unrecognized commands are
        handled. It is the primary extension point for adding role-specific
        command logic. It also handles the `@run` command if tools are enabled.

        Args:
            env: The environment.
        """
        handle_echo_commands(env)
        handle_autonomy_commands(env)
        if self._tools:
            handle_run_commands(env)

    def chat(self, prompt: ChatThread) -> ChatStream:
        """
        Processes a user's prompt and returns a response stream.

        This method implements the main interaction loop for the agent:
        1. It sets up the environment and registers tools.
        2. It calls `parse_prompt()` to set the full prompt thread, load session
           data from history, and extract commands from the prompt.
        3. It calls `handle_prompt()` to execute commands and populate the context.
        4. It handles unrecognized commands.
        5. It streams any status messages generated by commands.
        6. It generates a response from the model unless the prompt was swallowed.
        7. It saves the session state.

        Args:
            prompt: The full prompt thread from the user's client.

        Returns:
            A model stream with the generated response.
        """
        if not prompt or prompt[-1].intent != ChatIntent.PROMPT:
            raise ValueError("The last message in the thread must be a PROMPT.")

        env = Environment()
        env[ProjectEnv].configure(self._project_library)
        env[ModelEnv].configure(self._model_library, self._model)
        env[AutonomyEnv].configure(self._autonomy, self._autonomy_profiles)
        env[ToolEnv].register_all(self._tools)

        self.parse_prompt(env, prompt)

        # Mark messages before processing to identify new ones later
        snapshot_mark = env[ContextEnv].builder.mark()

        self.handle_prompt(env)

        context_env = env[ContextEnv]
        builder = context_env.builder
        new_messages = builder.extension(snapshot_mark)

        # Stream any status messages added during command processing.
        for message in new_messages:
            if message.intent == ChatIntent.STATUS:
                yield from message.stream()

        if not env[PromptEnv].swallowed:
            autonomy = env[AutonomyEnv].get()
            permit = autonomy.start(env)

            while True:
                generation_mark = builder.mark()
                model = env[ModelEnv].get()
                model_stream = model.generate(builder.build())
                yield from context_env.record(model_stream)

                # Handle autorun if enabled and tools are available
                if not autonomy.autorun or not self._tools:
                    break

                execution_mark = builder.mark()
                tools_executed = False
                for message in builder.extension(generation_mark):
                    if message.intent == ChatIntent.RESPONSE:
                        if execute_tool_calls(env, message.content) > 0:
                            tools_executed = True

                is_valid = True
                if tools_executed:
                    is_valid = permit.valid(env)

                # Stream any status messages generated by tool execution and autonomy checks
                for message in builder.extension(execution_mark):
                    if message.intent == ChatIntent.STATUS:
                        yield from message.stream()

                if not tools_executed or not is_valid:
                    break

        # Save session state for the current session ID.
        self._session_history.save(env)

__all__ = [
    'Agent',
]
