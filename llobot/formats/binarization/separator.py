"""
Separator-based binarization format.
"""
from __future__ import annotations
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.thread import ChatThread
from llobot.formats.binarization import BinarizationFormat
from llobot.utils.values import ValueTypeMixin

class SeparatorBinarizationFormat(BinarizationFormat, ValueTypeMixin):
    """
    A binarization format that merges consecutive messages of the same group.

    It maps SYSTEM, EXAMPLE_PROMPT, PROMPT, and STATUS to PROMPT.
    It maps EXAMPLE_RESPONSE and RESPONSE to RESPONSE.

    Consecutive messages that map to the same intent are joined. If they originate
    from the same intent (or both are SYSTEM/STATUS), they are joined with an
    empty line ('\n\n'). Otherwise, they are joined with the configured separator.
    Empty or whitespace-only messages are discarded.
    """
    _separator: str

    def __init__(self, separator: str = '\n\n---\n\n'):
        """
        Initializes the format.

        Args:
            separator: String used to join merged messages.
        """
        self._separator = separator

    def binarize_intent(self, intent: ChatIntent) -> ChatIntent:
        if intent in [ChatIntent.SYSTEM, ChatIntent.EXAMPLE_PROMPT, ChatIntent.PROMPT, ChatIntent.STATUS]:
            return ChatIntent.PROMPT
        if intent in [ChatIntent.EXAMPLE_RESPONSE, ChatIntent.RESPONSE]:
            return ChatIntent.RESPONSE
        raise ValueError(f"Unknown intent for binarization: {intent}")

    def binarize_chat(self, chat: ChatThread) -> ChatThread:
        messages: list[ChatMessage] = []
        last_original_intent: ChatIntent | None = None
        system_status = {ChatIntent.SYSTEM, ChatIntent.STATUS}

        for message in chat:
            # Skip empty or whitespace-only messages
            if not message.content or not message.content.strip():
                continue

            binarized = self.binarize_message(message)
            if not messages:
                messages.append(binarized)
                last_original_intent = message.intent
            else:
                last = messages[-1]
                if last.intent == binarized.intent:
                    is_same_source = (message.intent == last_original_intent) or \
                                     (message.intent in system_status and last_original_intent in system_status)
                    sep = '\n\n' if is_same_source else self._separator

                    new_content = last.content + sep + binarized.content
                    messages[-1] = ChatMessage(last.intent, new_content)
                    last_original_intent = message.intent
                else:
                    messages.append(binarized)
                    last_original_intent = message.intent
        return ChatThread(messages)

__all__ = [
    'SeparatorBinarizationFormat',
]
