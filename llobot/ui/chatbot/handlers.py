from __future__ import annotations
import logging
from llobot.chats import ChatRole
from llobot.models.streams import ModelStream
import llobot.ui.chatbot.requests
from llobot.ui.chatbot.requests import ChatbotRequest
import llobot.ui.chatbot.commands
from llobot.ui.chatbot.commands import ChatbotCommand
import llobot.time
import llobot.models.streams

_logger = logging.getLogger(__name__)

def _cutoff_footer(request: ChatbotRequest) -> ModelStream:
    return llobot.models.streams.completed(f'`:{llobot.time.format(request.cutoff)}`')

def handle_ok(request: ChatbotRequest) -> ModelStream:
    # Strip the last message that contains the !ok command
    chat_to_save = request.prompt[:-1]
    if len(chat_to_save) < 2:
        return llobot.models.streams.error('Nothing to save. An example must contain at least a prompt and a response.')
    request.chatbot.role.handle_ok(chat_to_save, request.project, request.cutoff)
    return llobot.models.streams.ok('Saved.')

def handle_prompt(request: ChatbotRequest) -> ModelStream:
    assembled = llobot.ui.chatbot.requests.assemble(request)
    output = request.model.generate(assembled)

    if request.has_implicit_cutoff and len(request.prompt) == 1:
        output += _cutoff_footer(request)

    def on_error():
        _logger.error(f'Exception in {request.model.name} model ({request.chatbot.role.name} role).', exc_info=True)

    return output | llobot.models.streams.handler(callback=on_error)

def handle(request: ChatbotRequest) -> ModelStream:
    if request.project and len(request.prompt) == 1 and request.has_implicit_cutoff:
        request.project.root.refresh()

    if request.command == ChatbotCommand.OK:
        return handle_ok(request)
    else:
        return handle_prompt(request)

__all__ = [
    'handle_ok',
    'handle_prompt',
    'handle',
]
