"""
User interface for chatbot interaction.

This package provides a user interface layer that exposes llobot's core logic
as a virtual model that can be served via Ollama or OpenAI protocols.

The main entry point is the `create` function, which wraps a `Role` into a
`Chatbot`, which is then exposed as a `ChatbotModel`.

Submodules
----------

model
    Implements `ChatbotModel` that wraps a `Chatbot` instance.
"""

from __future__ import annotations
from llobot.roles import Role
from llobot.models import Model
from llobot.projects import Project

class Chatbot:
    _role: Role

    def __init__(self, role: Role):
        self._role = role

    @property
    def role(self) -> Role:
        return self._role

def create(role: Role) -> Model:
    from llobot.ui.chatbot.model import ChatbotModel
    chatbot = Chatbot(role)
    return ChatbotModel(chatbot)

__all__ = [
    'Chatbot',
    'create',
]
