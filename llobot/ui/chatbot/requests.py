from __future__ import annotations
from datetime import datetime
from llobot.chats import ChatBranch, ChatMetadata
from llobot.projects import Project
from llobot.models import Model
from llobot.contexts import Context
from llobot.ui.chatbot import Chatbot
import llobot.ui.chatbot.chats
import llobot.ui.chatbot.commands
from llobot.ui.chatbot.commands import ChatbotCommand
import llobot.time
import llobot.models.streams

class ChatbotRequest:
    _chatbot: Chatbot
    _command: ChatbotCommand | None
    _prompt: ChatBranch
    _project: Project | None
    _cutoff: datetime
    _has_implicit_cutoff: bool
    _model: Model

    def __init__(self, *,
        chatbot: Chatbot,
        command: ChatbotCommand | None,
        prompt: ChatBranch,
        project: Project | None,
        cutoff: datetime | None,
        model: Model
    ):
        self._chatbot = chatbot
        self._command = command
        self._prompt = prompt
        self._project = project
        self._has_implicit_cutoff = cutoff is None
        self._cutoff = cutoff or llobot.time.now()
        self._model = model
    
    @property
    def chatbot(self) -> Chatbot:
        return self._chatbot
    
    @property
    def command(self) -> ChatbotCommand | None:
        return self._command
    
    @property
    def prompt(self) -> ChatBranch:
        return self._prompt
    
    @property
    def project(self) -> Project | None:
        return self._project
    
    @property
    def cutoff(self) -> datetime:
        return self._cutoff
    
    @property
    def has_implicit_cutoff(self) -> bool:
        return self._has_implicit_cutoff
    
    @property
    def model(self) -> Model:
        return self._model

def _decode_project(chatbot: Chatbot, name: str) -> Project:
    for project in chatbot.projects:
        found = project.find(name)
        if found:
            return found
    llobot.models.streams.fail(f'No such project: {name}')

def parse(chatbot: Chatbot, prompt: ChatBranch) -> ChatbotRequest:
    chat_info = llobot.ui.chatbot.chats.parse(prompt)
    header = chat_info.header

    project = _decode_project(chatbot, header.project) if header.project else None
    model = chatbot.models[header.model] if header.model else chatbot.model
    
    if header.options:
        model.validate_options(header.options)
        model = model.configure(header.options)
    
    cutoff = header.cutoff or chat_info.cutoff
    command = header.command or chat_info.command

    return ChatbotRequest(
        chatbot=chatbot,
        command=command,
        prompt=chat_info.prompt,
        project=project,
        cutoff=cutoff,
        model=model
    )

def chat_metadata(request: ChatbotRequest) -> ChatMetadata:
    return ChatMetadata(
        model=request.model.name,
        options=request.model.options,
        cutoff=request.cutoff
    )

def stuff(request: ChatbotRequest, prompt: ChatBranch | None = None) -> Context:
    prompt = prompt or request.prompt
    return request.chatbot.role.stuff(
        prompt=prompt,
        project=request.project,
        cutoff=request.cutoff,
        budget=request.model.context_budget
    )

def assemble(request: ChatbotRequest, prompt: ChatBranch | None = None) -> ChatBranch:
    return stuff(request, prompt).chat + (prompt or request.prompt)

__all__ = [
    'ChatbotRequest',
    'parse',
    'chat_metadata',
    'stuff',
    'assemble',
]
