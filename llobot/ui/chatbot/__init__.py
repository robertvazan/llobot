"""
User interface for chatbot interaction.

This package provides a user interface layer that translates raw chat messages
into structured requests for llobot's core logic. It handles parsing of
special commands, headers, and other metadata embedded in user prompts.

The main entry point is the `create` function, which wraps a `Role` and a `Model`
into a `Chatbot`, which is then exposed as a `ChatbotModel`. This virtual model
can be served via Ollama or OpenAI protocols.

Submodules
----------

chats
    Parses `Chatbot` specific elements from a `ChatBranch`.
commands
    Parses `!command` from user messages.
cutoffs
    Parses `:timestamp` from model responses to pin knowledge version.
handlers
    Main request handler for `ChatbotModel`, dispatching commands.
headers
    Parses `~project:cutoff@model?options!command` headers from prompts.
model
    Implements `ChatbotModel` that wraps a `Chatbot` instance.
requests
    Parses a `ChatBranch` into a structured `ChatbotRequest`.
"""

from __future__ import annotations
from llobot.roles import Role
from llobot.models import Model
from llobot.models.catalogs import ModelCatalog
from llobot.projects import Project

class Chatbot:
    _role: Role
    _model: Model
    _models: ModelCatalog
    _projects: list[Project]

    def __init__(self, role: Role, model: Model, models: ModelCatalog | None = None, projects: list[Project] | None = None):
        self._role = role
        self._model = model
        self._models = (models or ModelCatalog()) | ModelCatalog(model)
        self._projects = projects or []

    @property
    def role(self) -> Role:
        return self._role

    @property
    def model(self) -> Model:
        return self._model

    @property
    def models(self) -> ModelCatalog:
        return self._models

    @property
    def projects(self) -> list[Project]:
        return self._projects

def create(role: Role, model: Model, models: ModelCatalog | None = None, projects: list[Project] | None = None) -> Model:
    from llobot.ui.chatbot.model import ChatbotModel
    chatbot = Chatbot(role, model, models, projects)
    return ChatbotModel(chatbot)

__all__ = [
    'Chatbot',
    'create',
]
