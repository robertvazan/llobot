from __future__ import annotations
import logging
from llobot.chats.thread import ChatThread
from llobot.models import Model
from llobot.models.streams import ModelStream, exception_stream
from llobot.roles import Role
from llobot.formats.submessages import SubmessageFormat, standard_submessage_format
from llobot.utils.values import ValueTypeMixin

_logger = logging.getLogger(__name__)

class RoleModel(Model, ValueTypeMixin):
    """
    A wrapper that exposes a `Role` as a `Model`.

    This allows roles to be used in any context where a `Model` is expected,
    such as in listeners that expose models via standard protocols.
    """
    _role: Role
    _format: SubmessageFormat

    def __init__(self, role: Role, *, submessage_format: SubmessageFormat | None = None):
        """
        Initializes the RoleModel.

        Args:
            role: The role to wrap.
            submessage_format: The submessage format to use. Defaults to the standard one.
        """
        self._role = role
        self._format = submessage_format or standard_submessage_format()

    @property
    def name(self) -> str:
        return self._role.name

    def generate(self, prompt: ChatThread) -> ModelStream:
        """
        Generates a response by invoking the role's chat method.

        This method wraps the role's chat logic with error handling. It catches exceptions
        during both the initial call to `role.chat()` and during the streaming of the response.
        Exceptions are logged, and an error is streamed to the client.

        It parses submessages in the incoming prompt and renders the outgoing stream
        into submessages. This allows roles to work with structured multi-message
        conversations while presenting a single-message interface.

        Args:
            prompt: The user's prompt as a chat thread.

        Returns:
            A model stream with the generated response
        """
        try:
            parsed_prompt = self._format.parse_chat(prompt)
            stream = self._role.chat(parsed_prompt)
            yield from self._format.render_stream(stream)
        except Exception as ex:
            _logger.error(f'Exception in {self._role.name} role.', exc_info=True)
            yield from exception_stream(ex)

__all__ = [
    'RoleModel',
]
