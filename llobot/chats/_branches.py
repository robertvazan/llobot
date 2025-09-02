from __future__ import annotations
import llobot.text
from ._intents import ChatIntent
from ._messages import ChatMessage

class ChatBranch:
    _messages: list[ChatMessage]
    _hash: int | None

    def __init__(self, messages: list[ChatMessage] = []):
        self._messages = messages
        self._hash = None

    @property
    def messages(self) -> list[ChatMessage]:
        return self._messages.copy()

    def __repr__(self) -> str:
        return str(self._messages)

    def __bool__(self) -> bool:
        return bool(self._messages)

    def __len__(self) -> int:
        return len(self._messages)

    def __eq__(self, other) -> bool:
        if not isinstance(other, ChatBranch):
            return NotImplemented
        return self._messages == other._messages

    def __hash__(self) -> int:
        if self._hash is None:
            self._hash = hash(tuple(self._messages))
        return self._hash

    @property
    def cost(self) -> int:
        return sum([message.cost for message in self], 0)

    @property
    def pretty_cost(self) -> str:
        cost = self.cost
        kb = cost / 1000
        if kb < 10:
            return f"{kb:.1f} KB"
        return f"{kb:.0f} KB"

    def __getitem__(self, key: int | slice) -> ChatMessage | ChatBranch:
        if isinstance(key, slice):
            return ChatBranch(self._messages[key])
        return self._messages[key]

    def __iter__(self) -> Iterator[ChatMessage]:
        return iter(self._messages)

    def __contains__(self, text: str) -> bool:
        return any((text in message.content) for message in self)

    def __add__(self, suffix: ChatBranch | ChatMessage | None) -> ChatBranch:
        if suffix is None:
            return self
        if isinstance(suffix, ChatMessage):
            suffix = suffix.branch()
        return ChatBranch(self._messages + suffix._messages)

    def to_builder(self) -> 'ChatBuilder':
        from ._builders import ChatBuilder
        builder = ChatBuilder()
        builder.add(self)
        return builder

    def as_example(self) -> ChatBranch:
        return ChatBranch([message.as_example() for message in self])

    def binarize(self, *, last: ChatIntent | None = None) -> ChatBranch:
        """
        Normalizes the chat branch into a strict alternating sequence of PROMPT and RESPONSE messages.

        This method performs several normalization steps:
        - Reorders prompt-session message pairs to session-prompt pairs.
        - Binarizes message intents to either PROMPT or RESPONSE.
        - Inserts "Okay" (RESPONSE) between consecutive PROMPT messages.
        - Inserts "Go on" (PROMPT) between consecutive RESPONSE messages.
        - Ensures the last message has the specified intent, appending "Go on" or "Okay" if necessary.

        Args:
            last: The expected intent of the last message. If None, the final message intent is not enforced.

        Returns:
            A new, normalized ChatBranch.
        """
        # Reorder prompt-session pairs
        reordered = []
        i = 0
        messages = self._messages
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
        binarized_messages = [message.binarize() for message in reordered]

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

    def monolithic(self) -> str:
        return llobot.text.concat(*(message.monolithic() for message in self))

    def __and__(self, other: ChatBranch) -> ChatBranch:
        from ._builders import ChatBuilder
        shared = ChatBuilder()
        for message1, message2 in zip(self, other):
            if message1 == message2:
                shared.add(message1)
            else:
                break
        return shared.build()
