from __future__ import annotations
from llobot.chats import ChatBranch, ChatBuilder
import llobot.ui.chatbot.headers
from llobot.ui.chatbot.headers import ChatbotHeader

class ChatbotChat:
    _header: ChatbotHeader
    _prompt: ChatBranch

    def __init__(self, *, header: ChatbotHeader, prompt: ChatBranch):
        self._header = header
        self._prompt = prompt

    @property
    def header(self) -> ChatbotHeader:
        return self._header

    @property
    def prompt(self) -> ChatBranch:
        return self._prompt

def strip(chat: ChatBranch) -> ChatBranch:
    clean = ChatBuilder()
    if not chat:
        return clean.build()

    clean.add(chat[0].with_content(llobot.ui.chatbot.headers.strip(chat[0].content)))
    if len(chat) > 1:
        clean.add(chat[1:])
    return clean.build()

def parse(chat: ChatBranch) -> ChatbotChat:
    header = llobot.ui.chatbot.headers.parse(chat[0].content) if chat else ChatbotHeader()
    if not header:
        header = ChatbotHeader()

    prompt = strip(chat)
    return ChatbotChat(header=header, prompt=prompt)

__all__ = [
    'ChatbotChat',
    'strip',
    'parse',
]
