from __future__ import annotations
import re
from typing import Iterator
from llobot.chats.builder import ChatBuilder
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.stream import ChatStream
from llobot.chats.thread import ChatThread
from llobot.formats.submessages import SubmessageFormat
from llobot.utils.values import ValueTypeMixin

# Matches '[//]: # (Intent)' where Intent is alphanumeric/dashes
_COMMENT_RE = re.compile(r'\[//\]: # \(([a-zA-Z0-9-]+)\)')
_MARKER_PREFIX = "[//]: #"

class LinkCommentSubmessageFormat(SubmessageFormat, ValueTypeMixin):
    """
    A submessage format using Markdown comments as delimiters.

    Each message is wrapped in a pair of comments:
    - `[//]: # (Intent)`
    - `[//]: # (End)`

    Messages with intents other than `RESPONSE` or `STATUS` are additionally
    wrapped in collapsible `<details>` blocks. This allows embedding structured
    messages in a single response message without cluttering the UI.

    For example:

    ```markdown
    [//]: # (System)

    <details>
    <summary>System</summary>

    Nested message content

    </details>

    [//]: # (End)
    ```

    `RESPONSE` and `STATUS` messages are not wrapped in `<details>`. Consecutive
    submessages are separated by an empty line.

    Lines in the content that conflict with the delimiter format are escaped
    by prepending `Escaped-` to the comment content. For example,
    `[//]: # (End)` in the content becomes `[//]: # (Escaped-End)`.
    """

    def _escape_line(self, line: str) -> str:
        """Escapes a line if it looks like a delimiter comment."""
        clean_line = line.rstrip('\n')
        match = _COMMENT_RE.fullmatch(clean_line)
        if match:
            escaped = f'[//]: # (Escaped-{match.group(1)})'
            return escaped + ('\n' if line.endswith('\n') else '')
        return line

    def render(self, chat: ChatThread) -> str:
        """
        Renders a chat thread into a single string using link-comment delimiters.

        Args:
            chat: The chat thread to render.

        Returns:
            A single string representing the thread with nested messages.
        """
        submessages = []
        for message in chat:
            # Header
            block = [f'[//]: # ({message.intent})', '']

            # Content
            content = message.content
            if message.intent not in [ChatIntent.RESPONSE, ChatIntent.STATUS]:
                content = f'<details>\n<summary>{message.intent}</summary>\n\n{content}\n\n</details>'

            for line in content.splitlines():
                block.append(self._escape_line(line))

            # Ensure separation between content and closing marker
            if content.endswith('\n'):
                block.append('')

            # Footer
            block.append('')
            block.append('[//]: # (End)')

            submessages.append('\n'.join(block))

        return '\n\n'.join(submessages)

    def _split_tokens(self, stream: ChatStream) -> ChatStream:
        """
        Splits string items in the stream so that newlines only appear at the
        end of tokens.
        """
        for item in stream:
            if isinstance(item, ChatIntent):
                yield item
            else:
                parts = item.split('\n')
                for i, part in enumerate(parts):
                    if i < len(parts) - 1:
                        yield part + '\n'
                    elif part:
                        yield part

    def _escape_stream(self, stream: ChatStream) -> ChatStream:
        """
        Filters the stream to escape lines that look like comment delimiters.

        It buffers tokens at the start of lines to check against the marker prefix.
        If a match is found, it buffers the whole line to escape it.
        Otherwise, it streams tokens through.
        """
        buffer: list[str] = []
        at_start_of_line = True

        def flush() -> Iterator[str]:
            nonlocal buffer
            if buffer:
                yield "".join(buffer)
                buffer = []

        for token in stream:
            if isinstance(token, ChatIntent):
                yield from flush()
                yield token
                at_start_of_line = True
                continue

            # String token
            if at_start_of_line:
                buffer.append(token)
                current = "".join(buffer)

                if len(current) >= len(_MARKER_PREFIX):
                    if current.startswith(_MARKER_PREFIX):
                        # It looks like a comment. Buffer until newline.
                        if current.endswith('\n'):
                            # End of line. Escape and yield.
                            yield self._escape_line(current)
                            buffer = []
                    else:
                        # Enough characters, does not start with prefix. Flush.
                        yield from flush()
                        if not token.endswith('\n'):
                            at_start_of_line = False
                else:
                    # Not enough characters yet.
                    if current.endswith('\n'):
                        # Line ended, was too short to be a marker. Flush.
                        yield from flush()
            else:
                # Not at start of line, just pass through
                yield token
                if token.endswith('\n'):
                    at_start_of_line = True

        yield from flush()

    def render_stream(self, stream: ChatStream) -> ChatStream:
        """
        Renders a model stream into a single message stream using link-comment delimiters.

        Args:
            stream: The model stream to format.

        Returns:
            A new stream containing the formatted output as a single message.
        """
        current_intent: ChatIntent | None = None
        in_submessage = False
        is_first = True

        yield ChatIntent.RESPONSE

        stream = self._split_tokens(stream)
        stream = self._escape_stream(stream)

        for item in stream:
            if isinstance(item, ChatIntent):
                if in_submessage:
                    # Close previous message
                    yield '\n\n'
                    if current_intent not in [ChatIntent.RESPONSE, ChatIntent.STATUS]:
                        yield '</details>\n\n'
                    yield '[//]: # (End)'

                if not is_first:
                    yield '\n\n'
                is_first = False

                current_intent = item
                in_submessage = True

                yield f'[//]: # ({current_intent})\n\n'
                if current_intent not in [ChatIntent.RESPONSE, ChatIntent.STATUS]:
                    yield f'<details>\n<summary>{current_intent}</summary>\n\n'

            else:
                yield item

        if in_submessage:
            yield '\n\n'
            if current_intent not in [ChatIntent.RESPONSE, ChatIntent.STATUS]:
                yield '</details>\n\n'
            yield '[//]: # (End)'

    def parse(self, formatted: str) -> ChatThread:
        """
        Parses a formatted string with link-comment delimiters back into a chat thread.

        Args:
            formatted: The string to parse.

        Returns:
            A `ChatThread` object with the expanded submessages.
        """
        builder = ChatBuilder()
        lines = formatted.splitlines()

        current_intent: ChatIntent | None = None
        buffer: list[str] = []

        for line in lines:
            match = _COMMENT_RE.fullmatch(line)
            if match:
                content = match.group(1)
                if content.startswith('Escaped-'):
                    # Unescape and treat as content
                    if current_intent:
                        buffer.append(f'[//]: # ({content[8:]})')
                elif content == 'End':
                    # End of message
                    if current_intent:
                        self._add_parsed_message(builder, current_intent, buffer)
                        current_intent = None
                        buffer = []
                else:
                    # Start of new message
                    if current_intent:
                        # Close previous message implicitly
                        self._add_parsed_message(builder, current_intent, buffer)

                    try:
                        current_intent = ChatIntent.parse(content)
                        buffer = []
                    except ValueError:
                        # Not a valid intent, treat as content
                        if current_intent:
                            buffer.append(line)
            else:
                if current_intent:
                    buffer.append(line)

        if current_intent:
            self._add_parsed_message(builder, current_intent, buffer)

        return builder.build()

    def _add_parsed_message(self, builder: ChatBuilder, intent: ChatIntent, lines: list[str]):
        # Assume strict format from render()
        # [0] is empty, [-1] is empty
        if len(lines) >= 2:
            inner = lines[1:-1]
        else:
            inner = []

        if intent not in [ChatIntent.RESPONSE, ChatIntent.STATUS]:
            # Wrapped in details
            # Expected: <details>, <summary>...</summary>, '', ...content..., '', </details>
            if len(inner) >= 5:
                 inner = inner[3:-2]

        builder.add(ChatMessage(intent, '\n'.join(inner)))

__all__ = [
    'LinkCommentSubmessageFormat',
]
