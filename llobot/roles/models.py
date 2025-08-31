from __future__ import annotations
import logging
from llobot.chats import ChatBranch
from llobot.models import Model
from llobot.models.streams import ModelStream
from llobot.roles import Role
import llobot.models.streams

_logger = logging.getLogger(__name__)

class RoleModel(Model):
    _role: Role

    def __init__(self, role: Role):
        self._role = role

    @property
    def name(self) -> str:
        return f'bot/{self._role.name}'

    def generate(self, prompt: ChatBranch) -> ModelStream:
        """
        Generates a response by invoking the role's chat method.

        This method wraps the role's chat logic with error handling. It catches exceptions
        during both the initial call to `role.chat()` and during the streaming of the response.
        Exceptions are logged, and an error is streamed to the client.

        Args:
            prompt: The user's prompt as a chat branch.

        Returns:
            A model stream with the generated response
        """
        try:
            yield from self._role.chat(prompt)
        except Exception as ex:
            _logger.error(f'Exception in {self._role.name} role.', exc_info=True)
            yield from llobot.models.streams.exception(ex)

__all__ = [
    'RoleModel',
]
