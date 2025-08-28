from __future__ import annotations
import logging
from llobot.chats import ChatBranch
from llobot.models import Model
from llobot.models.streams import ModelStream
from llobot.ui.chatbot import Chatbot
import llobot.ui.chatbot.requests
import llobot.models.streams
import llobot.time

_logger = logging.getLogger(__name__)

def _cutoff_footer(request: llobot.ui.chatbot.requests.ChatbotRequest) -> ModelStream:
    return llobot.models.streams.completed(f'`:{llobot.time.format(request.cutoff)}`')

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
            request = llobot.ui.chatbot.requests.parse(self._chatbot, prompt)

            if request.project and len(request.prompt) == 1 and request.has_implicit_cutoff:
                request.project.refresh()

            assembled = llobot.ui.chatbot.requests.assemble(request)
            model = request.chatbot.role.model
            output = model.generate(assembled)

            if request.has_implicit_cutoff and len(request.prompt) == 1:
                output += _cutoff_footer(request)

            def on_error():
                _logger.error(f'Exception in {model.name} model ({request.chatbot.role.name} role).', exc_info=True)

            return output | llobot.models.streams.handler(callback=on_error)
        except Exception as ex:
            _logger.error(f'Exception in {self.name} model.', exc_info=True)
            return llobot.models.streams.exception(ex)

__all__ = [
    'ChatbotModel',
]
