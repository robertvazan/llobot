from __future__ import annotations
import logging
from llobot.chats import ChatRole
from llobot.models.streams import ModelStream
from .requests import ChatbotRequest, chat_metadata, assemble
from .commands import ChatbotCommand
from .info import handle_info
import llobot.time
import llobot.models.streams

_logger = logging.getLogger(__name__)

def _cutoff_footer(request: ChatbotRequest) -> ModelStream:
    return llobot.models.streams.completed(f'`:{llobot.time.format(request.cutoff)}`')

def handle_ok(request: ChatbotRequest) -> ModelStream:
    if len(request.prompt) < 3:
        return llobot.models.streams.error('Nothing to save.')
    
    metadata_branch = request.prompt[:-1].with_metadata(chat_metadata(request))
    request.chatbot.role.save_example(metadata_branch, request.project)
    return llobot.models.streams.ok('Saved.')

def handle_echo(request: ChatbotRequest) -> ModelStream:
    # We don't want any header or cutoff here, because output of echo might be pasted into other chat interfaces.
    return llobot.models.streams.completed(assemble(request).monolithic())

def handle_prompt(request: ChatbotRequest) -> ModelStream:
    assembled = assemble(request)
    output = request.model.generate(assembled)
    
    def on_complete(stream: ModelStream):
        response = ChatRole.ASSISTANT.message(stream.response())
        full_chat = (request.prompt + response).with_metadata(chat_metadata(request))
        request.chatbot.role.save_chat(full_chat, request.project)

    save_filter = llobot.models.streams.notify(on_complete)
    inner = output | save_filter
    if request.has_implicit_cutoff and len(request.prompt) == 1:
        inner += _cutoff_footer(request)
    
    def on_error():
        _logger.error(f'Exception in {request.model.name} model ({request.chatbot.role.name} role).', exc_info=True)

    return inner | llobot.models.streams.handler(callback=on_error)

def handle(request: ChatbotRequest) -> ModelStream:
    if request.project and len(request.prompt) == 1 and request.has_implicit_cutoff:
        request.project.root.refresh()

    if request.command == ChatbotCommand.OK:
        return handle_ok(request)
    elif request.command == ChatbotCommand.ECHO:
        return handle_echo(request)
    elif request.command == ChatbotCommand.INFO:
        return handle_info(request)
    else:
        return handle_prompt(request)
