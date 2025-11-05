"""
Details/summary-based monolithic format.
"""
from __future__ import annotations
from llobot.chats.message import ChatMessage
from llobot.chats.thread import ChatThread
from llobot.formats.monolithic import MonolithicFormat
from llobot.utils.text import concat_documents
from llobot.utils.values import ValueTypeMixin

class DetailsMonolithicFormat(MonolithicFormat, ValueTypeMixin):
    """
    A monolithic format that wraps each message in a <details> element.

    The message intent is used as the summary text.
    """
    def render(self, chat: ChatThread) -> str:
        """
        Renders a chat thread by concatenating messages formatted with <details>.

        Args:
            chat: The chat thread to render.

        Returns:
            A single string with all messages formatted and joined.
        """
        rendered_messages = []
        for message in chat:
            if message.content.strip():
                rendered = f'<details>\n<summary>{message.intent}</summary>\n\n{message.content}\n\n</details>'
                rendered_messages.append(rendered)
        return concat_documents(*rendered_messages)

__all__ = [
    'DetailsMonolithicFormat',
]
