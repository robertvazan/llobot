from __future__ import annotations
from datetime import datetime
from llobot.chats import ChatBranch, ChatBuilder, ChatRole
import llobot.ui.chatbot.headers
from llobot.ui.chatbot.headers import ChatbotHeader
import llobot.ui.chatbot.cutoffs
import llobot.ui.chatbot.commands
from llobot.ui.chatbot.commands import ChatbotCommand
import llobot.models.streams

class ChatbotChat:
    _header: ChatbotHeader
    _cutoff: datetime | None
    _command: ChatbotCommand | None
    _prompt: ChatBranch

    def __init__(self, *, header: ChatbotHeader, cutoff: datetime | None, command: ChatbotCommand | None, prompt: ChatBranch):
        self._header = header
        self._cutoff = cutoff
        self._command = command
        self._prompt = prompt

    @property
    def header(self) -> ChatbotHeader:
        return self._header
    
    @property
    def cutoff(self) -> datetime | None:
        return self._cutoff
    
    @property
    def command(self) -> ChatbotCommand | None:
        return self._command
    
    @property
    def prompt(self) -> ChatBranch:
        return self._prompt

def strip(chat: ChatBranch) -> ChatBranch:
    clean = ChatBuilder()
    if not chat:
        return clean.build()

    clean.add(chat[0].with_content(llobot.ui.chatbot.headers.strip(chat[0].content)))
    if len(chat) >= 2:
        clean.add(chat[1].with_content(llobot.ui.chatbot.cutoffs.strip(chat[1].content)))
    if len(chat) >= 3:
        for message in chat[2:-1]:
            clean.add(message)
        clean.add(chat[-1].with_content(llobot.ui.chatbot.commands.strip(chat[-1].content)))
    return clean.build()

def parse(chat: ChatBranch) -> ChatbotChat:
    header = llobot.ui.chatbot.headers.parse(chat[0].content) if chat else ChatbotHeader()
    if not header:
        header = ChatbotHeader()

    cutoff = None
    command = None

    if len(chat) > 1:
        if header.command:
            llobot.models.streams.fail('Followup message even though command was given.')
        
        automatic_cutoff = llobot.ui.chatbot.cutoffs.parse(chat[1].content)
        if automatic_cutoff:
            if header.cutoff:
                llobot.models.streams.fail('Duplicate cutoff.')
            cutoff = automatic_cutoff

        for message in chat[1:-1]:
            if message.role == ChatRole.USER and llobot.ui.chatbot.commands.parse(message.content):
                llobot.models.streams.fail('Followup message after a command.')

        if chat and chat[-1].role == ChatRole.USER:
            command = llobot.ui.chatbot.commands.parse(chat[-1].content)
        
    prompt = strip(chat)
    return ChatbotChat(header=header, cutoff=cutoff, command=command, prompt=prompt)

__all__ = [
    'ChatbotChat',
    'strip',
    'parse',
]
