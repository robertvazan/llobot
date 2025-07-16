from __future__ import annotations
from datetime import datetime
from llobot.chats import ChatBranch, ChatBuilder, ChatRole
from .headers import ChatbotHeader, parse as parse_header, strip as strip_header
from .cutoffs import parse as parse_cutoff, strip as strip_cutoff
from .commands import ChatbotCommand, parse as parse_command, strip as strip_command
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
    def header(self) -> ChatbotHeader: return self._header
    
    @property
    def cutoff(self) -> datetime | None: return self._cutoff
    
    @property
    def command(self) -> ChatbotCommand | None: return self._command
    
    @property
    def prompt(self) -> ChatBranch: return self._prompt

def strip(chat: ChatBranch) -> ChatBranch:
    clean = ChatBuilder()
    if not chat:
        return clean.build()

    clean.add(chat[0].with_content(strip_header(chat[0].content)))
    if len(chat) >= 2:
        clean.add(chat[1].with_content(strip_cutoff(chat[1].content)))
    if len(chat) >= 3:
        for message in chat[2:-1]:
            clean.add(message)
        clean.add(chat[-1].with_content(strip_command(chat[-1].content)))
    return clean.build()

def parse(chat: ChatBranch) -> ChatbotChat:
    header = parse_header(chat[0].content) if chat else ChatbotHeader()
    if not header:
        header = ChatbotHeader()

    cutoff = None
    command = None

    if len(chat) > 1:
        if header.command:
            llobot.models.streams.fail('Followup message even though command was given.')
        
        automatic_cutoff = parse_cutoff(chat[1].content)
        if automatic_cutoff:
            if header.cutoff:
                llobot.models.streams.fail('Duplicate cutoff.')
            cutoff = automatic_cutoff

        for message in chat[1:-1]:
            if message.role == ChatRole.USER and parse_command(message.content):
                llobot.models.streams.fail('Followup message after a command.')
        command = parse_command(chat[-1].content)
        
    prompt = strip(chat)
    return ChatbotChat(header=header, cutoff=cutoff, command=command, prompt=prompt)
