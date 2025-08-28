from __future__ import annotations
from llobot.chats import ChatBranch
from llobot.projects import Project
from llobot.ui.chatbot import Chatbot
import llobot.ui.chatbot.chats

class ChatbotRequest:
    _chatbot: Chatbot
    _prompt: ChatBranch
    _project: Project | None

    def __init__(self, *,
        chatbot: Chatbot,
        prompt: ChatBranch,
        project: Project | None,
    ):
        self._chatbot = chatbot
        self._prompt = prompt
        self._project = project

    @property
    def chatbot(self) -> Chatbot:
        return self._chatbot

    @property
    def prompt(self) -> ChatBranch:
        return self._prompt

    @property
    def project(self) -> Project | None:
        return self._project

def _decode_project(chatbot: Chatbot, name: str) -> Project:
    project = chatbot.projects.get(name)
    if project:
        return project
    raise KeyError(f'No such project: {name}')

def parse(chatbot: Chatbot, prompt: ChatBranch) -> ChatbotRequest:
    chat_info = llobot.ui.chatbot.chats.parse(prompt)
    header = chat_info.header

    project = _decode_project(chatbot, header.project) if header.project else None

    return ChatbotRequest(
        chatbot=chatbot,
        prompt=chat_info.prompt,
        project=project,
    )

def stuff(request: ChatbotRequest, prompt: ChatBranch | None = None) -> ChatBranch:
    prompt = prompt or request.prompt
    return request.chatbot.role.stuff(
        prompt=prompt,
        project=request.project,
    )

def assemble(request: ChatbotRequest, prompt: ChatBranch | None = None) -> ChatBranch:
    return stuff(request, prompt) + (prompt or request.prompt)

__all__ = [
    'ChatbotRequest',
    'parse',
    'stuff',
    'assemble',
]
