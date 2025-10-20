"""
Selected model.
"""
from __future__ import annotations
from pathlib import Path
from llobot.environments.persistent import PersistentEnv
from llobot.models import Model
from llobot.models.library import ModelLibrary
from llobot.models.library.empty import EmptyModelLibrary
from llobot.utils.fs import read_text, write_text

class ModelEnv(PersistentEnv):
    """
    An environment component that holds the currently selected model.
    It can be persisted by saving the key of the selected model.
    """
    _library: ModelLibrary
    _default: Model | None
    _selected_key: str | None
    _selected_model: Model | None

    def __init__(self):
        self._library = EmptyModelLibrary()
        self._default = None
        self._selected_key = None
        self._selected_model = None

    def configure(self, library: ModelLibrary, default: Model):
        """
        Configures the model library and default model to use.
        """
        self._library = library
        self._default = default

    def select(self, key: str) -> Model | None:
        """
        Looks up a model by key and selects it if found.

        Args:
            key: The key to look up a model in the configured library.

        Returns:
            The matching model that was found, or `None`.
        """
        found = self._library.lookup(key)
        if found:
            self._selected_key = key
            self._selected_model = found
        return found

    def get(self) -> Model:
        """
        Gets the selected model, or the default if none is selected.

        Returns:
            The selected or default `Model` instance.

        Raises:
            ValueError: If no model is selected and no default is configured.
        """
        if self._selected_model:
            return self._selected_model
        if self._default:
            return self._default
        raise ValueError("No model selected and no default model configured.")

    def save(self, directory: Path):
        """
        Saves the key of the selected model to `model.txt`.
        """
        if self._selected_key:
            write_text(directory / 'model.txt', self._selected_key + '\n')

    def load(self, directory: Path):
        """
        Loads a model key from `model.txt`, clearing any prior selection.

        This method assumes that a model library has already been configured.
        If the `model.txt` file doesn't exist, the selection is cleared.

        Args:
            directory: The directory to load the state from.

        Raises:
            ValueError: If a key from `model.txt` does not match any model.
        """
        self._selected_key = None
        self._selected_model = None

        path = directory / 'model.txt'
        if not path.exists():
            return

        key = read_text(path).strip()
        if key:
            if not self.select(key):
                raise ValueError(f"Model key '{key}' from model.txt not found in library.")

__all__ = [
    'ModelEnv',
]
