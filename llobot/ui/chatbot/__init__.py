"""
User interface for chatbot interaction.

This package provides a user interface layer that translates raw chat messages
into structured requests for llobot's core logic. It handles parsing of
special commands, headers, and other metadata embedded in user prompts.

The main entry point is the `create` function, which wraps a `Role` into a
`Chatbot`, which is then exposed as a `ChatbotModel`. This virtual model can be
served via Ollama or OpenAI protocols.

Submodules
----------

chats
    Parses `Chatbot` specific elements from a `ChatBranch`.
cutoffs
    Parses `:timestamp` from model responses to pin knowledge version.
headers
    Parses `~project:cutoff` headers from prompts.
model
    Implements `ChatbotModel` that wraps a `Chatbot` instance.
requests
    Parses a `ChatBranch` into a structured `ChatbotRequest`.
"""

from __future__ import annotations
from llobot.roles import Role
from llobot.models import Model
from llobot.projects import Project

class Chatbot:
    _role: Role
    _projects: dict[str, Project]

    def __init__(self, role: Role, projects: list[Project] | None = None):
        self._role = role
        self._projects = {p.name: p for p in projects} if projects else {}

    @property
    def role(self) -> Role:
        return self._role

    @property
    def projects(self) -> dict[str, Project]:
        return self._projects

def create(role: Role, projects: list[Project] | None = None) -> Model:
    from llobot.ui.chatbot.model import ChatbotModel
    chatbot = Chatbot(role, projects)
    return ChatbotModel(chatbot)

__all__ = [
    'Chatbot',
    'create',
]
