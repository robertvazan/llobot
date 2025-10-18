from __future__ import annotations
from llobot.chats.thread import ChatThread
from llobot.chats.builder import ChatBuilder
from llobot.models import Model
from llobot.chats.stream import ChatStream
from llobot.prompts import Prompt
from llobot.roles import Role
from llobot.formats.prompts import PromptFormat, standard_prompt_format


class Chatbot(Role):
    """
    A simple role that prepends a system prompt to the user's prompt.
    """
    _name: str
    _model: Model
    _system: str
    _prompt_format: PromptFormat

    def __init__(self, name: str, model: Model, *,
        prompt: str | Prompt = '',
        prompt_format: PromptFormat = standard_prompt_format(),
    ):
        """
        Initializes the Chatbot role.

        Args:
            name: The name of the role.
            model: The language model to use.
            prompt: The system prompt to use. Defaults to empty.
            prompt_format: The format for the system prompt.
        """
        self._name = name
        self._model = model
        self._system = str(prompt)
        self._prompt_format = prompt_format

    @property
    def name(self) -> str:
        return self._name

    def chat(self, prompt: ChatThread) -> ChatStream:
        """
        Processes user's prompt and returns response as a stream.

        It prepends the system prompt to the user's prompt and sends it to the model.

        Args:
            prompt: The user's prompt as a chat thread.

        Returns:
            A model stream with the generated response.
        """
        builder = ChatBuilder()
        system_chat = self._prompt_format.render_chat(self._system)
        builder.add(system_chat)
        builder.add(prompt)
        return self._model.generate(builder.build())

__all__ = [
    'Chatbot',
]
