from __future__ import annotations
from pathlib import Path
from llobot.chats.intent import ChatIntent
from llobot.chats.markdown import load_chat_from_markdown, save_chat_to_markdown
from llobot.chats.stream import ChatStream
from llobot.chats.thread import ChatThread
from llobot.chats.builder import ChatBuilder
from llobot.chats.message import ChatMessage
from llobot.environments.persistent import PersistentEnv

class ContextEnv(PersistentEnv):
    """
    An environment component for accumulating chat messages.
    The accumulated context can be persisted to disk.

    Last prompt message is only kept in PromptEnv while it is being processed,
    so that the context can be populated before the prompt message is added.
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

    def add(self, branch: ChatThread | ChatMessage | None):
        """
        Adds messages to the context.
        """
        self._builder.add(branch)

    def coerce(self, visible: ChatThread):
        """
        Coerces the context to match visible conversation history.

        This method is intended to help roles respond reasonably when a user edits
        the chat history or navigates back in time. It aligns the persisted
        context with the visible history from the user's client.

        The method works by pairing messages from the visible history with
        messages in the current context based on matching intents in sequence.
        If a content mismatch is found in a pair, the context is truncated
        at that point and the remainder of the visible history is appended.

        If the visible history is a prefix of the context, any remaining
        "conversational" messages (PROMPT, RESPONSE, SESSION, STATUS) in the
        context are truncated.

        If the context is a prefix of the visible history, the extra messages
        from the visible history are appended to the context.

        Args:
            visible: The chat history visible to the user, excluding the latest
                     prompt.
        """
        context_messages = self._builder.build()
        conv_intents = {ChatIntent.PROMPT, ChatIntent.RESPONSE, ChatIntent.SESSION, ChatIntent.STATUS}

        # Find corresponding messages by intent.
        pairs: list[tuple[int, int]] = []  # (visible_idx, context_idx)
        context_cursor = 0
        for visible_idx, visible_msg in enumerate(visible):
            found_match = False
            for context_idx in range(context_cursor, len(context_messages)):
                if context_messages[context_idx].intent == visible_msg.intent:
                    # Check if we skipped any conversational messages
                    skipped = context_messages[context_cursor:context_idx]
                    if any(m.intent in conv_intents for m in skipped):
                        # Cannot skip conversational messages. Match invalid.
                        break

                    pairs.append((visible_idx, context_idx))
                    context_cursor = context_idx + 1
                    found_match = True
                    break

            if not found_match:
                break

        # Check for content mismatch.
        for visible_idx, context_idx in pairs:
            if visible[visible_idx].content != context_messages[context_idx].content:
                # Mismatch found. Truncate context and append rest of visible history.
                self._builder.undo(mark=context_idx)
                self._builder.add(visible[visible_idx:])
                return

        last_visible_idx, last_context_idx = pairs[-1] if pairs else (-1, -1)

        # Truncate extra messages from context if there are conversational ones.
        tail = context_messages[last_context_idx + 1:]
        if any(m.intent in conv_intents for m in tail):
            self._builder.undo(mark=last_context_idx + 1)

        # Append extra visible messages.
        if last_visible_idx < len(visible) - 1:
            self._builder.add(visible[last_visible_idx + 1:])

    def record(self, stream: ChatStream) -> ChatStream:
        """
        Records a model stream while passing it through.
        """
        return self._builder.record(stream)

    def build(self) -> ChatThread:
        """
        Builds the final `ChatThread` from the accumulated messages.
        """
        return self._builder.build()

    def save(self, directory: Path):
        """
        Saves the current context to `context.md`.

        The file is created even if it's empty.
        """
        save_chat_to_markdown(directory / 'context.md', self.build())

    def load(self, directory: Path):
        """
        Loads context from `context.md`.

        If the file doesn't exist, the context is left empty.
        """
        path = directory / 'context.md'
        if path.exists():
            chat = load_chat_from_markdown(path)
            self._builder = chat.to_builder()
        else:
            self._builder = ChatBuilder()

__all__ = [
    'ContextEnv',
]
