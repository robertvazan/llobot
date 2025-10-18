from __future__ import annotations
from pathlib import Path
from llobot.chats.archives.markdown import load_chat_as_markdown, save_chat_as_markdown
from llobot.chats.branches import ChatBranch
from llobot.chats.builders import ChatBuilder
from llobot.chats.messages import ChatMessage
from llobot.environments.persistent import PersistentEnv

class ContextEnv(PersistentEnv):
    """
    An environment component for accumulating chat messages.
    The accumulated context can be persisted to disk.
    """
    _builder: ChatBuilder

    def __init__(self):
        self._builder = ChatBuilder()

    @property
    def populated(self) -> bool:
        """
        Checks if any messages have been added to the context.
        """
        return bool(self._builder)

    @property
    def builder(self) -> ChatBuilder:
        """
        The underlying `ChatBuilder` for this context.
        """
        return self._builder

    def add(self, branch: ChatBranch | ChatMessage | None):
        """
        Adds messages to the context.
        """
        self._builder.add(branch)

    def build(self) -> ChatBranch:
        """
        Builds the final `ChatBranch` from the accumulated messages.
        """
        return self._builder.build()

    def save(self, directory: Path):
        """
        Saves the current context to `context.md`.

        The file is created even if the context is empty.
        """
        save_chat_as_markdown(directory / 'context.md', self.build())

    def load(self, directory: Path):
        """
        Loads context from `context.md`.

        If the file doesn't exist, the context is left empty.
        """
        path = directory / 'context.md'
        if path.exists():
            branch = load_chat_as_markdown(path)
            self._builder = branch.to_builder()
        else:
            self._builder = ChatBuilder()

__all__ = [
    'ContextEnv',
]
