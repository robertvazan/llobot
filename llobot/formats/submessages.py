from __future__ import annotations
from functools import cache
from typing import Iterable
import re
from llobot.chats.branches import ChatBranch
from llobot.chats.messages import ChatMessage
from llobot.chats.intents import ChatIntent
from llobot.chats.builders import ChatBuilder
from llobot.utils.text import concat_documents

class SubmessageFormat:
    """
    Base class for submessage formats.

    Submessage formats pack a `ChatBranch` into a single string.
    They can also parse the formatted string back into a `ChatBranch`.
    """
    def render(self, chat: ChatBranch) -> str:
        """
        Renders a chat branch into a single string.

        Args:
            chat: The chat branch to render.

        Returns:
            A single string representing the branch.
        """
        raise NotImplementedError

    def render_stream(self, stream: 'ModelStream') -> 'ModelStream':
        """
        Renders a model stream into a single message stream.

        This method processes an incoming stream of message chunks and intents,
        which may represent multiple messages, and wraps each message in a
        submessage format. It yields a single continuous stream of strings
        that represents a single message with an implicit RESPONSE intent.
        This is useful for displaying structured, multi-part responses
        incrementally.

        Args:
            stream: The model stream to format, an iterable of strings and
                    `ChatIntent` objects.

        Returns:
            A new stream of strings containing the formatted output.
        """
        raise NotImplementedError

    def parse(self, formatted: str) -> ChatBranch:
        """
        Parses a formatted string back into a chat branch.

        Args:
            formatted: The string to parse.

        Returns:
            A `ChatBranch` object.
        """
        raise NotImplementedError

    def parse_chat(self, chat: ChatBranch) -> ChatBranch:
        """
        Parses submessages within RESPONSE messages of a chat branch.

        Args:
            chat: The chat branch to parse.

        Returns:
            A new `ChatBranch` with submessages expanded.
        """
        builder = ChatBuilder()
        for message in chat:
            if message.intent == ChatIntent.RESPONSE:
                builder.add(self.parse(message.content))
            else:
                builder.add(message)
        return builder.build()

@cache
def details_submessage_format() -> SubmessageFormat:
    """
    Creates a submessage format using HTML details/summary tags.

    Each message in the branch with an intent other than `RESPONSE` is
    wrapped in a collapsible `<details>` block. The content of `RESPONSE`
    messages is included directly. This allows embedding structured messages
    in a single response message without cluttering the UI.

    For example:

    ```markdown
    Preceding response content

    <details>
    <summary>Nested message: System</summary>

    Nested message content

    [//]: # (end of nested message)
    </details>

    Following response content
    ```

    Consecutive submessages are separated by an empty line.
    `RESPONSE` messages are not wrapped. They are separated from other
    messages (both wrapped and unwrapped) by an empty line.

    Returns:
        A `SubmessageFormat` instance.
    """
    from llobot.models.streams import ModelStream
    class DetailsSubmessageFormat(SubmessageFormat):
        def render(self, chat: ChatBranch) -> str:
            submessages = []
            for message in chat:
                if message.intent == ChatIntent.RESPONSE:
                    submessages.append(message.content)
                else:
                    summary = f'Nested message: {message.intent}'
                    block = f'<details>\n<summary>{summary}</summary>\n\n{message.content}\n\n[//]: # (end of nested message)\n</details>'
                    submessages.append(block)

            # Join consecutive submessages with an empty line.
            return concat_documents(*submessages)

        def render_stream(self, stream: ModelStream) -> ModelStream:
            in_details = False
            is_first_message = True

            for item in stream:
                if isinstance(item, ChatIntent):
                    if in_details:
                        yield '\n\n[//]: # (end of nested message)\n</details>'
                        in_details = False

                    if not is_first_message:
                        yield '\n\n'
                    is_first_message = False

                    if item != ChatIntent.RESPONSE:
                        summary = f'Nested message: {item}'
                        yield f'<details>\n<summary>{summary}</summary>\n\n'
                        in_details = True

                elif isinstance(item, str) and item:
                    is_first_message = False
                    yield item

            if in_details:
                yield '\n\n[//]: # (end of nested message)\n</details>'

        def parse(self, formatted: str) -> ChatBranch:
            builder = ChatBuilder()
            state = 'response'
            intent = None
            lines = []

            def flush_response():
                content = '\n'.join(lines).strip()
                if content:
                    builder.add(ChatMessage(ChatIntent.RESPONSE, content))
                lines.clear()

            def flush_submessage():
                content = '\n'.join(lines).strip()
                builder.add(ChatMessage(intent, content))
                lines.clear()

            for line in formatted.splitlines():
                if state == 'response':
                    if line == '<details>':
                        state = 'details'
                    lines.append(line)
                elif state == 'details':
                    if line.startswith('<summary>Nested message: ') and line.endswith('</summary>'):
                        summary = line.removeprefix('<summary>Nested message: ').removesuffix('</summary>')
                        try:
                            intent = ChatIntent.parse(summary)
                            lines.pop()
                            flush_response()
                            state = 'submessage'
                        except ValueError:
                            lines.append(line)
                            state = 'response'
                    else:
                        lines.append(line)
                        state = 'response'
                elif state == 'submessage':
                    if line == '[//]: # (end of nested message)':
                        state = 'end_marker'
                    else:
                        lines.append(line)
                elif state == 'end_marker':
                    if line == '</details>':
                        flush_submessage()
                        intent = None
                        state = 'response'
                    else:
                        lines.append('[//]: # (end of nested message)')
                        lines.append(line)
                        state = 'submessage'

            if state in ['submessage', 'end_marker']:
                flush_submessage()
            else:
                flush_response()

            return builder.build()

    return DetailsSubmessageFormat()

@cache
def standard_submessage_format() -> SubmessageFormat:
    """Returns the standard submessage format."""
    return details_submessage_format()

__all__ = [
    'SubmessageFormat',
    'details_submessage_format',
    'standard_submessage_format',
]
