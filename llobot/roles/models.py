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
        role = self._role
        try:
            output = role.chat(prompt)

            # def on_error():
            #     _logger.error(f'Exception while processing response stream in {role.name} role.', exc_info=True)

            # return output | llobot.models.streams.handler(callback=on_error)
            return output
        except Exception as ex:
            _logger.error(f'Exception in {role.name} role.', exc_info=True)
            return llobot.models.streams.exception(ex)

__all__ = [
    'RoleModel',
]
