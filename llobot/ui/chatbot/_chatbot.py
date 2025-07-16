from __future__ import annotations
from llobot.roles import Role
from llobot.models import Model
from llobot.models.catalogs import ModelCatalog
from llobot.projects import Project
from .model import ChatbotModel

class Chatbot:
    _role: Role
    _model: Model
    _models: ModelCatalog
    _projects: list[Project]

    def __init__(self, role: Role, model: Model, models: ModelCatalog, projects: list[Project]):
        self._role = role
        self._model = model
        self._models = models | ModelCatalog(model)
        self._projects = projects

    @property
    def role(self) -> Role: return self._role
    
    @property
    def model(self) -> Model: return self._model

    @property
    def models(self) -> ModelCatalog: return self._models
    
    @property
    def projects(self) -> list[Project]: return self._projects

def create(role: Role, model: Model, models: ModelCatalog, projects: list[Project]) -> Model:
    chatbot = Chatbot(role, model, models, projects)
    return ChatbotModel(chatbot)
