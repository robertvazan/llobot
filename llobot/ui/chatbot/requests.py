from __future__ import annotations
from datetime import datetime
from llobot.chats import ChatBranch
from llobot.projects import Project
from llobot.ui.chatbot import Chatbot
import llobot.ui.chatbot.chats
import llobot.time

class ChatbotRequest:
    _chatbot: Chatbot
    _prompt: ChatBranch
    _project: Project | None
    _cutoff: datetime | None
    _has_implicit_cutoff: bool

    def __init__(self, *,
        chatbot: Chatbot,
        prompt: ChatBranch,
        project: Project | None,
        cutoff: datetime | None,
    ):
        self._chatbot = chatbot
        self._prompt = prompt
        self._project = project
        self._has_implicit_cutoff = cutoff is None
        self._cutoff = cutoff

    @property
    def chatbot(self) -> Chatbot:
        return self._chatbot

    @property
    def prompt(self) -> ChatBranch:
        return self._prompt

    @property
    def project(self) -> Project | None:
        return self._project

    @property
    def cutoff(self) -> datetime:
        # Initialize cutoff to current time at the last possible moment,
        # so that the cutoff is not earlier than timestamp of just refreshed knowledge.
        if self._cutoff is None:
            self._cutoff = llobot.time.now()
        return self._cutoff

    @property
    def has_implicit_cutoff(self) -> bool:
        return self._has_implicit_cutoff

def _decode_project(chatbot: Chatbot, name: str) -> Project:
    project = chatbot.projects.get(name)
    if project:
        return project
    raise KeyError(f'No such project: {name}')

def parse(chatbot: Chatbot, prompt: ChatBranch) -> ChatbotRequest:
    chat_info = llobot.ui.chatbot.chats.parse(prompt)
    header = chat_info.header

    project = _decode_project(chatbot, header.project) if header.project else None
    cutoff = header.cutoff or chat_info.cutoff

    return ChatbotRequest(
        chatbot=chatbot,
        prompt=chat_info.prompt,
        project=project,
        cutoff=cutoff,
    )

def stuff(request: ChatbotRequest, prompt: ChatBranch | None = None) -> ChatBranch:
    prompt = prompt or request.prompt
    return request.chatbot.role.stuff(
        prompt=prompt,
        project=request.project,
        cutoff=request.cutoff,
    )

def assemble(request: ChatbotRequest, prompt: ChatBranch | None = None) -> ChatBranch:
    return stuff(request, prompt) + (prompt or request.prompt)

__all__ = [
    'ChatbotRequest',
    'parse',
    'stuff',
    'assemble',
]
