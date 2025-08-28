from __future__ import annotations
import logging
from llobot.chats import ChatBranch
from llobot.models import Model
from llobot.models.streams import ModelStream
from llobot.ui.chatbot import Chatbot
import llobot.models.streams

_logger = logging.getLogger(__name__)

class ChatbotModel(Model):
    _chatbot: Chatbot

    def __init__(self, chatbot: Chatbot):
        self._chatbot = chatbot

    @property
    def name(self) -> str:
        return f'bot/{self._chatbot.role.name}'

    @property
    def context_budget(self) -> int:
        # This doesn't matter. Just propagate one from the primary model.
        return self._chatbot.role.model.context_budget

    def generate(self, prompt: ChatBranch) -> ModelStream:
        try:
            role = self._chatbot.role
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
    'ChatbotModel',
]
