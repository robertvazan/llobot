from __future__ import annotations
from datetime import datetime
from llobot.chats import ChatBranch, ChatBuilder
import llobot.ui.chatbot.headers
from llobot.ui.chatbot.headers import ChatbotHeader
import llobot.ui.chatbot.cutoffs

class ChatbotChat:
    _header: ChatbotHeader
    _cutoff: datetime | None
    _prompt: ChatBranch

    def __init__(self, *, header: ChatbotHeader, cutoff: datetime | None, prompt: ChatBranch):
        self._header = header
        self._cutoff = cutoff
        self._prompt = prompt

    @property
    def header(self) -> ChatbotHeader:
        return self._header

    @property
    def cutoff(self) -> datetime | None:
        return self._cutoff

    @property
    def prompt(self) -> ChatBranch:
        return self._prompt

def strip(chat: ChatBranch) -> ChatBranch:
    clean = ChatBuilder()
    if not chat:
        return clean.build()

    clean.add(chat[0].with_content(llobot.ui.chatbot.headers.strip(chat[0].content)))
    if len(chat) > 1:
        clean.add(chat[1].with_content(llobot.ui.chatbot.cutoffs.strip(chat[1].content)))
        if len(chat) > 2:
            clean.add(chat[2:])
    return clean.build()

def parse(chat: ChatBranch) -> ChatbotChat:
    header = llobot.ui.chatbot.headers.parse(chat[0].content) if chat else ChatbotHeader()
    if not header:
        header = ChatbotHeader()

    cutoff = None

    if len(chat) > 1:
        automatic_cutoff = llobot.ui.chatbot.cutoffs.parse(chat[1].content)
        if automatic_cutoff:
            if header.cutoff:
                raise ValueError('Duplicate cutoff.')
            cutoff = automatic_cutoff

    prompt = strip(chat)
    return ChatbotChat(header=header, cutoff=cutoff, prompt=prompt)

__all__ = [
    'ChatbotChat',
    'strip',
    'parse',
]
