from __future__ import annotations
from functools import cache
from typing import Iterable
import re
from llobot.chats import ChatBranch, ChatMessage, ChatIntent, ChatBuilder
import llobot.text

class SubmessageFormatter:
    """
    Base class for submessage formatters.

    Submessage formatters pack a `ChatBranch` into a single string.
    They can also parse the formatted string back into a `ChatBranch`.
    """
    def format(self, chat: ChatBranch) -> str:
        """
        Formats a chat branch into a single string.

        Args:
            chat: The chat branch to format.

        Returns:
            A single string representing the branch.
        """
        raise NotImplementedError

    def format_stream(self, stream: 'ModelStream') -> 'ModelStream':
        """
        Formats a model stream into a single message stream.

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

_BACKTICK_RE = re.compile(r'^(`{3,})')

@cache
def details() -> SubmessageFormatter:
    """
    Creates a submessage formatter using HTML details/summary tags.

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

    </details>

    <details>
    <summary>Nested message: Affirmation</summary>

    Okay

    </details>

    Following response content
    ```

    Consecutive submessages are separated by an empty line.
    `RESPONSE` messages are not wrapped. They are separated from other
    messages (both wrapped and unwrapped) by an empty line.

    Returns:
        A `SubmessageFormatter` instance.
    """
    from llobot.models.streams import ModelStream
    class DetailsSubmessageFormatter(SubmessageFormatter):
        def format(self, chat: ChatBranch) -> str:
            submessages = []
            for message in chat:
                if message.intent == ChatIntent.RESPONSE:
                    submessages.append(message.content)
                else:
                    summary = f'Nested message: {message.intent}'
                    block = f'<details>\n<summary>{summary}</summary>\n\n{message.content}\n\n</details>'
                    submessages.append(block)

            # Join consecutive submessages with an empty line.
            return llobot.text.concat(*submessages)

        def format_stream(self, stream: ModelStream) -> ModelStream:
            in_details = False
            is_first_message = True

            for item in stream:
                if isinstance(item, ChatIntent):
                    if in_details:
                        yield '\n\n</details>'
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
                yield '\n\n</details>'

        def parse(self, formatted: str) -> ChatBranch:
            builder = ChatBuilder()
            in_submessage = False
            details_depth = 0
            current_intent = None
            content_lines = []
            in_code_block = False
            backtick_count = 0

            def flush_response():
                content = '\n'.join(content_lines).strip()
                if content:
                    builder.add(ChatMessage(ChatIntent.RESPONSE, content))
                content_lines.clear()

            for line in formatted.splitlines():
                if in_code_block:
                    if line == '`' * backtick_count:
                        in_code_block = False
                    content_lines.append(line)
                    continue

                match = _BACKTICK_RE.match(line)
                if match:
                    in_code_block = True
                    backtick_count = len(match.group(1))
                    content_lines.append(line)
                    continue

                if line == '<details>':
                    details_depth += 1
                    content_lines.append(line)
                elif line == '</details>':
                    if in_submessage and details_depth == 1:
                        message_content = '\n'.join(content_lines).strip()
                        builder.add(ChatMessage(current_intent, message_content))
                        content_lines.clear()
                        in_submessage = False
                        current_intent = None
                        details_depth -= 1
                    else:
                        details_depth = max(0, details_depth - 1)
                        content_lines.append(line)
                elif line.startswith('<summary>Nested message: ') and line.endswith('</summary>'):
                    if not in_submessage and details_depth == 1 and content_lines and content_lines[-1] == '<details>':
                        summary_content = line.removeprefix('<summary>Nested message: ').removesuffix('</summary>')
                        try:
                            intent = ChatIntent.parse(summary_content)
                            content_lines.pop()  # remove '<details>'
                            flush_response()
                            in_submessage = True
                            current_intent = intent
                        except ValueError:
                            content_lines.append(line)
                    else:
                        content_lines.append(line)
                else:
                    content_lines.append(line)

            flush_response()
            return builder.build()

    return DetailsSubmessageFormatter()

@cache
def standard() -> SubmessageFormatter:
    """Returns the standard submessage formatter."""
    return details()

__all__ = [
    'SubmessageFormatter',
    'details',
    'standard',
]
