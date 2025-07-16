from __future__ import annotations
import logging
from llobot.chats import ChatBranch
from llobot.models import Model
from llobot.models.streams import ModelStream, ModelException
from ._chatbot import Chatbot
from .requests import parse as parse_request
from .handlers import handle
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
        return self._chatbot.model.context_budget

    def generate(self, prompt: ChatBranch) -> ModelStream:
        try:
            request = parse_request(self._chatbot, prompt)
            return handle(request)
        except ModelException as ex:
            return ex.stream
        except Exception as ex:
            _logger.error(f'Exception in {self.name} model.', exc_info=True)
            return llobot.models.streams.exception(ex)
