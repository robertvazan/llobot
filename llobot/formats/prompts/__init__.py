"""
System prompt formatting.

This package provides the `PromptFormat` base class and implementations for
rendering system prompts into chat messages. The main purpose is to convert a
`Prompt` object or a raw string into a `ChatThread` that can be prepended to
the conversation history.

Submodules
----------

plain
    A simple pass-through format.
grouped
    A format that groups H2 sections into details/summary blocks.
reminder
    A format that extracts reminders from the prompt.
"""
from __future__ import annotations
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.thread import ChatThread
from llobot.prompts import Prompt

class PromptFormat:
    """
    Base class for prompt formats.
    """
    def render(self, prompt: str | Prompt) -> str:
        """
        Renders a prompt as a string.

        Args:
            prompt: The prompt object or string to render.

        Returns:
            The rendered prompt as a string.
        """
        raise NotImplementedError

    def render_chat(self, prompt: str | Prompt) -> ChatThread:
        """
        Renders a prompt as a chat thread.

        This method renders the prompt to a string and then wraps it in a
        standard system message turn.

        Args:
            prompt: The prompt object or string to render.

        Returns:
            A `ChatThread` containing the rendered prompt.
        """
        rendered = self.render(prompt)
        if not rendered.strip():
            return ChatThread()
        return ChatThread([ChatMessage(ChatIntent.SYSTEM, rendered)])

def standard_prompt_format() -> PromptFormat:
    """
    Returns the standard prompt format.

    Returns:
        The standard `PromptFormat`.
    """
    from llobot.formats.prompts.grouped import GroupedPromptFormat
    return GroupedPromptFormat()

__all__ = [
    'PromptFormat',
    'standard_prompt_format',
]
