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
        try:
            role = self._role
            context = role.stuff(prompt=prompt)
            assembled = context + prompt
            model = role.model
            output = model.generate(assembled)

            def on_error():
                _logger.error(f'Exception in {model.name} model ({role.name} role).', exc_info=True)

            return output | llobot.models.streams.handler(callback=on_error)
        except Exception as ex:
            _logger.error(f'Exception in {self.name} model.', exc_info=True)
            return llobot.models.streams.exception(ex)

__all__ = [
    'RoleModel',
]
