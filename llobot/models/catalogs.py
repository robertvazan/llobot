from __future__ import annotations
from llobot.models import Model

class ModelCatalog:
    _models: list[Model]
    _aliases: dict[str, Model]

    def __init__(self, *models: Model):
        self._models = []
        self._aliases = {}
        for model in models:
            self.add(model)

    def add(self, model: Model):
        self._models = [other for other in self._models if other.name != model.name or other.options != model.options]
        self._models.append(model)

    def alias(self, model: Model | str, *aliases: str):
        if model is str:
            model = self[model]
        for alias in aliases:
            self._aliases[alias] = model

    def __len__(self) -> int:
        return len(self._models)

    def __iter__(self) -> Iterator[Model]:
        return iter(self._models)

    def get(self, name: str) -> Model | None:
        if name in self._aliases:
            return self._aliases[name]
        for model in self._models:
            if model.name == name:
                return model
        for model in self._models:
            for alias in model.aliases:
                if alias == name and not any(other != model and alias in other.aliases for other in self._models):
                    return model
        return None

    def __getitem__(self, name: str) -> Model:
        model = self.get(name)
        if not model:
            raise KeyError(f'No such model: {name}')
        return model

    def __or__(self, other: ModelCatalog) -> ModelCatalog:
        merged = ModelCatalog(*self._models)
        for model in other._models:
            merged.add(model)
        for alias, model in self._aliases.items():
            merged.alias(model, alias)
        for alias, model in other._aliases.items():
            merged.alias(model, alias)
        return merged

__all__ = [
    'ModelCatalog',
]

