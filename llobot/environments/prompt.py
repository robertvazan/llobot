"""
Prompt message environment component.
"""
from __future__ import annotations
import base64
import hashlib
from llobot.chats.thread import ChatThread
from llobot.chats.intent import ChatIntent

def _hash_thread(thread: ChatThread) -> str:
    """Computes a URL-safe base64 SHA-256 hash of the thread content."""
    hasher = hashlib.sha256()
    for message in thread:
        # Include intent to distinguish different message types
        chunk = f"{message.intent.value}:{message.content}".encode('utf-8')
        hasher.update(len(chunk).to_bytes(8, 'big'))
        hasher.update(chunk)
    b64 = base64.urlsafe_b64encode(hasher.digest()).decode('ascii')
    return b64[:40]

class PromptEnv:
    """
    Holds the full prompt thread and derives the session ID from it.

    The session ID is a hash of the full prompt thread. This component
    also provides access to the full prompt thread and to the content of the
    current (last) prompt message. It also calculates the hash of the previous
    session state to allow loading of historical sessions.
    """
    _full: ChatThread
    _hash: str | None
    _previous_hash: str | None
    _swallowed: bool

    def __init__(self):
        self._full = ChatThread()
        self._hash = None
        self._previous_hash = None
        self._swallowed = False

    def set(self, prompt: ChatThread):
        """
        Sets the full prompt thread and computes session hashes.

        Args:
            prompt: The full prompt thread visible to the user.
        """
        self._full = prompt
        self._hash = _hash_thread(prompt) if prompt else None
        self._previous_hash = self._calculate_previous_hash(prompt)
        self._swallowed = False

    def _calculate_previous_hash(self, prompt: ChatThread) -> str | None:
        """
        Calculates the hash of the previous session state.

        It searches backwards for the previous message with PROMPT intent
        (skipping the current one) and calculates the hash of the thread
        up to and including that message.
        """
        if not prompt:
            return None

        # Start searching from the second to last message
        for i in range(len(prompt) - 2, -1, -1):
            if prompt[i].intent == ChatIntent.PROMPT:
                return _hash_thread(prompt[:i+1])

        return None

    @property
    def hash(self) -> str | None:
        """
        The current session hash ID.

        Returns:
            The session hash, or `None` if the prompt is empty.
        """
        return self._hash

    @property
    def previous_hash(self) -> str | None:
        """
        The hash ID of the previous session state.

        Returns:
            The previous session hash, or `None` if there is no history.
        """
        return self._previous_hash

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
