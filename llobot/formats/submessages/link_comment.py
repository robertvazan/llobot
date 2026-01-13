from __future__ import annotations
import re
from llobot.chats.builder import ChatBuilder
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.stream import ChatStream
from llobot.chats.thread import ChatThread
from llobot.formats.submessages import SubmessageFormat
from llobot.utils.values import ValueTypeMixin

# Matches '[//]: # (Intent)' where Intent is alphanumeric/dashes
_COMMENT_RE = re.compile(r'\[//\]: # \(([a-zA-Z0-9-]+)\)')
_MARKER_PREFIX = "[//]:"

class LinkCommentSubmessageFormat(SubmessageFormat, ValueTypeMixin):
    """
    A submessage format using Markdown comments as delimiters.

    Each message starts with a header comment:
    - `[//]: # (Intent)`

    Messages with intents other than `RESPONSE` or `STATUS` are additionally
    wrapped in collapsible `<details>` blocks. This allows embedding structured
    messages in a single response message without cluttering the UI.

    If the first message has `RESPONSE` intent, it is treated as the
    default response and its header is omitted. This makes the output identical
    to the input for simple responses. Empty chats are not supported.

    For example:

    ```markdown
    Response content...

    [//]: # (System)

    <details>
    <summary>System</summary>

    Nested message content

    </details>

    [//]: # (Prompt)

    Next message content
    ```

    `RESPONSE` and `STATUS` messages are not wrapped in `<details>`. Consecutive
    submessages are separated by an empty line.

    Lines in the content that look like delimiter comments are escaped by
    prepending `Escaped-` to the comment content.
    """

    def _escape_line(self, line: str) -> str:
        """Escapes a line if it looks like a delimiter comment."""
        match = _COMMENT_RE.fullmatch(line)
        if match:
            return f'[//]: # (Escaped-{match.group(1)})'
        return line

    def _unescape_line(self, line: str) -> str:
        """Unescapes a line if it was escaped."""
        match = _COMMENT_RE.fullmatch(line)
        if match and match.group(1).startswith('Escaped-'):
            return f'[//]: # ({match.group(1)[8:]})'
        return line

    def render(self, chat: ChatThread) -> str:
        """
        Renders a chat thread into a single string using link-comment delimiters.

        Args:
            chat: The chat thread to render. Must not be empty.

        Returns:
            A single string representing the thread with nested messages.

        Raises:
            ValueError: If the chat is empty.
        """
        if not chat:
            raise ValueError("Chat cannot be empty")

        submessages = []
        for i, message in enumerate(chat):
            lines = []

            is_default_response = (i == 0 and message.intent == ChatIntent.RESPONSE)

            if not is_default_response:
                # Header
                lines.append(f'[//]: # ({message.intent})')
                lines.append('')

            # Content
            # Split content into lines. split('\n') returns an empty string as the last element
            # if the string ends with a newline, which corresponds to our line-oriented format.
            content_lines = message.content.split('\n')
            escaped_content_lines = [self._escape_line(line) for line in content_lines]

            if message.intent in [ChatIntent.RESPONSE, ChatIntent.STATUS]:
                lines.extend(escaped_content_lines)
            else:
                lines.append('<details>')
                lines.append(f'<summary>{message.intent}</summary>')
                lines.append('')
                lines.extend(escaped_content_lines)
                lines.append('')
                lines.append('</details>')

            submessages.append('\n'.join(lines))

        # Use double newline to separate submessages with an empty line.
        return '\n\n'.join(submessages)

    def _split_tokens(self, stream: ChatStream) -> ChatStream:
        """
        Splits string items in the stream so that newlines are yielded as separate tokens.
        """
        for item in stream:
            if isinstance(item, ChatIntent):
                yield item
            else:
                # Split by newline, keeping the delimiter.
                # Filter out empty strings which re.split might produce.
                parts = re.split(r'(\n)', item)
                for part in parts:
                    if part:
                        yield part

    def _join_comment_tokens(self, stream: ChatStream) -> ChatStream:
        """
        Joins tokens for a single line if that line starts with the comment prefix.
        """
        buffer = ""
        buffering = True

        for token in stream:
            if isinstance(token, ChatIntent) or token == '\n':
                if buffer:
                    yield buffer
                    buffer = ""
                yield token
                buffering = True
                continue

            # String token
            if not buffering:
                yield token
            else:
                buffer += token

                # Check if buffer matches prefix or is a prefix of it
                if buffer.startswith(_MARKER_PREFIX):
                    # It is a comment line so far. Keep buffering.
                    pass
                elif _MARKER_PREFIX.startswith(buffer):
                    # It looks like a comment line so far. Keep buffering.
                    pass
                else:
                    # Diverged. Flush buffer and switch to passthrough.
                    yield buffer
                    buffer = ""
                    buffering = False

        if buffer:
            yield buffer

    def _escape_stream(self, stream: ChatStream) -> ChatStream:
        """
        Filters the stream to escape lines that look like comment delimiters.
        Assumes stream has been processed by _split_tokens and _join_comment_tokens.
        """
        at_start_of_line = True

        for token in stream:
            if isinstance(token, ChatIntent) or token == '\n':
                yield token
                at_start_of_line = True
                continue

            # String token
            if at_start_of_line and token.startswith(_MARKER_PREFIX):
                yield self._escape_line(token)
            else:
                yield token

            at_start_of_line = False

    def _join_status_chunks(self, stream: ChatStream) -> ChatStream:
        """
        Buffers and joins all chunks inside status messages.
        """
        buffer: list[str] = []
        is_status = False

        for item in stream:
            if isinstance(item, ChatIntent):
                if buffer:
                    yield ''.join(buffer)
                    buffer.clear()

                yield item
                is_status = (item == ChatIntent.STATUS)
            elif is_status:
                buffer.append(item)
            else:
                yield item

        if buffer:
            yield ''.join(buffer)

    def render_stream(self, stream: ChatStream) -> ChatStream:
        """
        Renders a model stream into a single message stream using link-comment delimiters.

        Args:
            stream: The model stream to format.

        Returns:
            A new stream containing the formatted output as a single message.
        """
        current_intent: ChatIntent | None = None
        is_start_of_stream = True

        yield ChatIntent.RESPONSE

        stream = self._split_tokens(stream)
        stream = self._join_comment_tokens(stream)
        stream = self._escape_stream(stream)
        stream = self._join_status_chunks(stream)

        for item in stream:
            if isinstance(item, ChatIntent):
                if current_intent is not None:
                    # Close previous message
                    if current_intent not in [ChatIntent.RESPONSE, ChatIntent.STATUS]:
                        yield '\n\n</details>'

                    # Separator
                    yield '\n\n'

                current_intent = item
                is_default_response = is_start_of_stream and current_intent == ChatIntent.RESPONSE
                is_start_of_stream = False

                if not is_default_response:
                    yield f'[//]: # ({current_intent})\n\n'
                    if current_intent not in [ChatIntent.RESPONSE, ChatIntent.STATUS]:
                        yield f'<details>\n<summary>{current_intent}</summary>\n\n'

            else:
                yield item

        if current_intent is not None:
            if current_intent not in [ChatIntent.RESPONSE, ChatIntent.STATUS]:
                yield '\n\n</details>'

    def parse(self, formatted: str) -> ChatThread:
        """
        Parses a formatted string with link-comment delimiters back into a chat thread.

        Args:
            formatted: The string to parse.

        Returns:
            A `ChatThread` object with the expanded submessages.
        """
        builder = ChatBuilder()
        # split('\n') creates an empty string at the end if formatted ends with newline,
        # which matches our expectation for line processing.
        raw_lines = formatted.split('\n')

        blocks: list[tuple[ChatIntent | None, list[str]]] = []
        current_intent: ChatIntent | None = None
        current_lines: list[str] = []

        # Phase 1: Group lines into blocks by intent
        for line in raw_lines:
            match = _COMMENT_RE.fullmatch(line)
            # Ensure we don't treat escaped lines as headers
            if match and not match.group(1).startswith('Escaped-'):
                if current_intent or current_lines:
                    blocks.append((current_intent, current_lines))

                current_intent = ChatIntent.parse(match.group(1))
                current_lines = []
            else:
                current_lines.append(line)

        # Finish last block
        if current_intent or current_lines:
            blocks.append((current_intent, current_lines))

        # Phase 2: Process each block
        for i, (intent, lines) in enumerate(blocks):
            if intent is None:
                # Default response (implicit)
                intent = ChatIntent.RESPONSE
            else:
                # Explicit response or other intent
                # Remove empty line after header (inserted by render)
                if lines and lines[0] == '':
                    lines.pop(0)

            # Remove separator empty line at the end, except for the very last block
            # which doesn't have a separator appended in the formatted string logic
            if i < len(blocks) - 1:
                if lines and lines[-1] == '':
                    lines.pop(-1)

            # Unescape
            lines = [self._unescape_line(line) for line in lines]

            # Unwrap if necessary
            if intent not in [ChatIntent.RESPONSE, ChatIntent.STATUS]:
                # Check for wrapper structure:
                # 0: <details>
                # 1: <summary>...</summary>
                # 2: ''
                # ... content ...
                # -2: ''
                # -1: </details>
                if (len(lines) >= 5 and
                    lines[0] == '<details>' and
                    lines[1].startswith('<summary>') and
                    lines[2] == '' and
                    lines[-1] == '</details>' and
                    lines[-2] == ''):
                    lines = lines[3:-2]

            builder.add(ChatMessage(intent, '\n'.join(lines)))

        return builder.build()

__all__ = [
    'LinkCommentSubmessageFormat',
]
