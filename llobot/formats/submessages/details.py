"""
Submessage format using HTML details tags.
"""
from __future__ import annotations
from llobot.chats.branches import ChatBranch
from llobot.chats.messages import ChatMessage
from llobot.chats.intents import ChatIntent
from llobot.chats.builders import ChatBuilder
from llobot.formats.submessages import SubmessageFormat
from llobot.models.streams import ModelStream
from llobot.utils.text import concat_documents
from llobot.utils.values import ValueTypeMixin

class DetailsSubmessageFormat(SubmessageFormat, ValueTypeMixin):
    """
    A submessage format using HTML details/summary tags.

    Each message in the branch with an intent other than `RESPONSE` is
    wrapped in a collapsible `<details>` block. The content of `RESPONSE`
    messages is included directly. This allows embedding structured messages
    in a single response message without cluttering the UI.

    For example:

    ````markdown
    Preceding response content

    <details>
    <summary>Nested message: System</summary>

    Nested message content

    [//]: # (end of nested message)
    </details>

    Following response content
    ````

    Consecutive submessages are separated by an empty line.
    `RESPONSE` messages are not wrapped. They are separated from other
    messages (both wrapped and unwrapped) by an empty line.
    """

    def render(self, chat: ChatBranch) -> str:
        """
        Renders a chat branch into a single string using `<details>` tags.

        Args:
            chat: The chat branch to render.

        Returns:
            A single string representing the branch with nested messages.
        """
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
        """
        Renders a model stream into a single message stream using `<details>` tags.

        Args:
            stream: The model stream to format.

        Returns:
            A new stream of strings containing the formatted output.
        """
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
        """
        Parses a formatted string with `<details>` tags back into a chat branch.

        Args:
            formatted: The string to parse.

        Returns:
            A `ChatBranch` object with the expanded submessages.
        """
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

__all__ = [
    'DetailsSubmessageFormat',
]
