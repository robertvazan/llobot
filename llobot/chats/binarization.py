"""
Chat binarization logic.

This module provides functions to normalize a chat into a strict alternating
sequence of PROMPT and RESPONSE messages, which is required by many LLM APIs.
"""
from __future__ import annotations
from llobot.chats.intents import ChatIntent
from llobot.chats.messages import ChatMessage
from llobot.chats.branches import ChatBranch

def binarize_intent(intent: ChatIntent) -> ChatIntent:
    """
    Reduces the intent to either PROMPT or RESPONSE.
    """
    if intent in [ChatIntent.SYSTEM, ChatIntent.SESSION, ChatIntent.EXAMPLE_PROMPT, ChatIntent.PROMPT]:
        return ChatIntent.PROMPT
    if intent in [ChatIntent.AFFIRMATION, ChatIntent.EXAMPLE_RESPONSE, ChatIntent.RESPONSE]:
        return ChatIntent.RESPONSE
    raise ValueError(f"Unknown intent for binarization: {intent}")

def binarize_message(message: ChatMessage) -> ChatMessage:
    """
    Returns a new message with binarized intent (PROMPT or RESPONSE).
    """
    return ChatMessage(binarize_intent(message.intent), message.content)

def binarize_chat(chat: ChatBranch, *, last: ChatIntent | None = None) -> ChatBranch:
    """
    Normalizes a chat branch into a strict alternating sequence of PROMPT and RESPONSE messages.

    This method performs several normalization steps:
    - Reorders prompt-session message pairs to session-prompt pairs.
    - Binarizes message intents to either PROMPT or RESPONSE.
    - Inserts "Okay" (RESPONSE) between consecutive PROMPT messages.
    - Inserts "Go on" (PROMPT) between consecutive RESPONSE messages.
    - Ensures the last message has the specified intent, appending "Go on" or "Okay" if necessary.

    Args:
        chat: The chat branch to normalize.
        last: The expected intent of the last message. If None, the final message intent is not enforced.

    Returns:
        A new, normalized ChatBranch.
    """
    # Reorder prompt-session pairs
    reordered = []
    i = 0
    messages = chat.messages
    while i < len(messages):
        if (i + 1 < len(messages) and
                messages[i].intent == ChatIntent.PROMPT and
                messages[i+1].intent == ChatIntent.SESSION):
            reordered.append(messages[i+1])
            reordered.append(messages[i])
            i += 2
        else:
            reordered.append(messages[i])
            i += 1

    # Binarize all messages
    binarized_messages = [binarize_message(message) for message in reordered]

    # Insert fillers for consecutive messages of the same intent
    final_messages = []
    if binarized_messages:
        final_messages.append(binarized_messages[0])
        for i in range(1, len(binarized_messages)):
            prev_msg = final_messages[-1]
            curr_msg = binarized_messages[i]

            if prev_msg.intent == curr_msg.intent:
                if curr_msg.intent == ChatIntent.PROMPT:
                    final_messages.append(ChatMessage(ChatIntent.RESPONSE, "Okay"))
                else:  # RESPONSE
                    final_messages.append(ChatMessage(ChatIntent.PROMPT, "Go on"))

            final_messages.append(curr_msg)

    # Ensure last message has the required intent
    if last is not None:
        if not final_messages or final_messages[-1].intent != last:
            if last == ChatIntent.PROMPT:
                final_messages.append(ChatMessage(ChatIntent.PROMPT, "Go on"))
            else:  # RESPONSE
                final_messages.append(ChatMessage(ChatIntent.RESPONSE, "Okay"))

    return ChatBranch(final_messages)

__all__ = [
    'binarize_intent',
    'binarize_message',
    'binarize_chat',
]
