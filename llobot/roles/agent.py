from __future__ import annotations
from pathlib import Path
from llobot.chats.thread import ChatThread
from llobot.chats.intent import ChatIntent
from llobot.chats.stream import ChatStream
from llobot.commands.session import ensure_session_command, handle_session_commands
from llobot.commands.unrecognized import handle_unrecognized_commands
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
from llobot.models import Model
from llobot.projects.library import ProjectLibrary, ProjectLibraryPrecursor, coerce_project_library
from llobot.prompts import Prompt
from llobot.roles import Role
from llobot.utils.zones import Zoning

class Agent(Role):
    """
    A base role for agents that handle sessions, environment, and command execution.

    This class provides a framework for creating roles that interact with a user
    through a chat interface. It manages session state, command parsing, and
    context assembly. Subclasses can customize behavior by overriding methods
    for context stuffing, command handling, and prompt generation.
    """
    _name: str
    _model: Model
    _system: str
    _session_history: SessionHistory
    _prompt_format: PromptFormat
    _reminder_format: PromptFormat
    _project_library: ProjectLibrary

    def __init__(self, name: str, model: Model, *,
        prompt: str | Prompt = '',
        projects: ProjectLibraryPrecursor = (),
        session_history: SessionHistory | Zoning | Path | str = standard_session_history(),
        prompt_format: PromptFormat = standard_prompt_format(),
        reminder_format: PromptFormat = ReminderPromptFormat(),
    ):
        """
        Initializes the Agent role.

        Args:
            name: The name of the role.
            model: The language model to use.
            prompt: The system prompt.
            projects: A project library or a precursor for one.
            session_history: Session history storage.
            prompt_format: Format for the main system prompt.
            reminder_format: Format for reminder prompts.
        """
        self._name = name
        self._model = model
        self._system = str(prompt)
        self._project_library = coerce_project_library(projects)
        self._session_history = coerce_session_history(session_history)
        self._prompt_format = prompt_format
        self._reminder_format = reminder_format

    @property
    def name(self) -> str:
        return self._name

    def handle_prompt(self, env: Environment):
        """
        Processes commands and populates the environment.

        This method orchestrates command handling by ensuring a session is active,
        loading session history, and then delegating to `handle_setup`,
        `stuff`, and `handle_commands` for role-specific logic.

        Args:
            env: The environment to process commands in.
        """
        ensure_session_command(env)
        session_id = env[SessionEnv].get_id()
        if session_id:
            self._session_history.load(session_id, env)
        self.handle_setup(env)
        if not env[ContextEnv].populated:
            self.stuff(env)
        self.handle_commands(env)

    def handle_setup(self, env: Environment):
        """
        Hook for subclasses to prepare the environment before stuffing.

        This is called after project commands are handled but before the context
        is stuffed. It can be used to populate environment components that `stuff`
        depends on, such as loading a knowledge base.

        Args:
            env: The environment to prepare.
        """
        pass

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
        builder.budget = self._model.context_budget
        builder.add(self._prompt_format.render_chat(self._system))

    def remind(self, env: Environment):
        """
        Adds a reminder prompt to the context.

        This is typically used for the first turn in a conversation to reinforce
        the system prompt.

        Args:
            env: The environment to add the reminder to.
        """
        env[ContextEnv].add(self._reminder_format.render_chat(self._system))

    def handle_commands(self, env: Environment):
        """
        Hook for subclasses to add custom command handlers.

        This method is called after stuffing and before unrecognized commands are
        handled. It is the primary extension point for adding role-specific
        command logic.

        Args:
            env: The environment.
        """
        pass

    def chat(self, prompt: ChatThread) -> ChatStream:
        """
        Processes a user's prompt and returns a response stream.

        This method implements the main interaction loop for the agent:
        1. It sets up the environment and processes any session commands from the prompt.
        2. It parses commands from the user's latest message.
        3. It calls `handle_prompt()` to execute commands and populate the context.
        4. It handles unrecognized commands.
        5. If it's the first message, it adds a reminder prompt.
        6. It sends the final assembled context to the model and streams the response.
        7. It saves the session state.

        Args:
            prompt: The user's prompt as a chat thread.

        Returns:
            A model stream with the generated response.
        """
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
        self.handle_prompt(env)
        handle_unrecognized_commands(env)

        context_env = env[ContextEnv]
        if len(prompt) == 1:
            self.remind(env)
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
    'Agent',
]
