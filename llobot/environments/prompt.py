"""
Prompt message environment component.
"""
from __future__ import annotations
import base64
import hashlib
from llobot.chats.thread import ChatThread

class PromptEnv:
    """
    Holds the full prompt thread and derives the session ID from it.

    The session ID is a short hash of the initial prompt message. This component
    also provides access to the full prompt thread and to the content of the
    current (last) prompt message. It also tracks whether the prompt has been
    "swallowed" by a command, which signals that the agent should stop processing.
    """
    _full: ChatThread
    _hash: str | None
    _swallowed: bool

    def __init__(self):
        self._full = ChatThread()
        self._hash = None
        self._swallowed = False

    def set(self, prompt: ChatThread):
        """
        Sets the full prompt thread and computes the session hash from it.

        The session hash is derived from the content of the first message in the
        thread (the initial prompt).

        Args:
            prompt: The full prompt thread visible to the user.
        """
        self._full = prompt
        if prompt and prompt[0].content:
            hasher = hashlib.sha256(prompt[0].content.encode('utf-8'))
            b64 = base64.urlsafe_b64encode(hasher.digest()).decode('ascii')
            self._hash = b64[:40]
        else:
            self._hash = None
        self._swallowed = False

    @property
    def hash(self) -> str | None:
        """
        The session hash ID.

        Returns:
            The session hash, or `None` if the initial prompt is empty or undefined.
        """
        return self._hash

    @property
    def full(self) -> ChatThread:
        """
        The full prompt thread visible to the user.

        Returns:
            The prompt thread.
        """
        return self._full

    @property
    def current(self) -> str:
        """
        The content of the current (last) prompt message.

        Returns:
            The last message's content, or an empty string if the prompt thread is empty.
        """
        if not self._full:
            return ''
        return self._full[-1].content

    @property
    def swallowed(self) -> bool:
        """
        Whether the prompt has been swallowed by a command.

        If true, the agent should not query the model for a response.
        """
        return self._swallowed

    def swallow(self) -> None:
        """
        Swallows the prompt, preventing the agent from querying the model.
        """
        self._swallowed = True

__all__ = [
    'PromptEnv',
]
