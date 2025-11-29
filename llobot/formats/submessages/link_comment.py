from __future__ import annotations
import re
import secrets
from llobot.chats.builder import ChatBuilder
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.stream import ChatStream
from llobot.chats.thread import ChatThread
from llobot.formats.submessages import SubmessageFormat
from llobot.utils.values import ValueTypeMixin

# Matches '[//]: # (Intent: ID)'
_OPEN_RE = re.compile(r'\[//\]: # \(([^:]+): ([a-zA-Z0-9_-]+)\)')

def _new_id() -> str:
    """
    Generates a new unique ID for a submessage.
    """
    # 15 bytes gives 20 URL-safe base64 characters. 120 bits of entropy.
    return secrets.token_urlsafe(15)

class LinkCommentSubmessageFormat(SubmessageFormat, ValueTypeMixin):
    """
    A submessage format using Markdown comments with unique IDs as delimiters.

    Each message is wrapped in a pair of comments:
    - `[//]: # (Intent: ID)`
    - `[//]: # (ID)`

    where `ID` is a unique random identifier.

    Messages with intents other than `RESPONSE` or `STATUS` are additionally
    wrapped in collapsible `<details>` blocks. This allows embedding structured
    messages in a single response message without cluttering the UI.

    For example:

    ```markdown
    [//]: # (System: abcdef1234)

    <details>
    <summary>System</summary>

    Nested message content

    </details>

    [//]: # (abcdef1234)
    ```

    `RESPONSE` and `STATUS` messages are not wrapped in `<details>`. Consecutive
    submessages are separated by an empty line.
    """

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
            msg_id = _new_id()
            open_comment = f'[//]: # ({message.intent}: {msg_id})'
            close_comment = f'[//]: # ({msg_id})'

            if message.intent not in [ChatIntent.RESPONSE, ChatIntent.STATUS]:
                content = f'<details>\n<summary>{message.intent}</summary>\n\n{message.content}\n\n</details>'
            else:
                content = message.content

            block = f'{open_comment}\n\n{content}\n\n{close_comment}'
            submessages.append(block)

        return '\n\n'.join(submessages)

    def render_stream(self, stream: ChatStream) -> ChatStream:
        """
        Renders a model stream into a single message stream using link-comment delimiters.

        Args:
            stream: The model stream to format.

        Returns:
            A new stream containing the formatted output as a single message.
        """
        in_message = False
        is_first_message = True
        current_id = ''
        current_intent: ChatIntent | None = None

        yield ChatIntent.RESPONSE

        for item in stream:
            if isinstance(item, ChatIntent):
                if in_message:
                    # Close previous message
                    yield '\n\n'
                    if current_intent and current_intent not in [ChatIntent.RESPONSE, ChatIntent.STATUS]:
                        yield '</details>\n\n'

                    yield f'[//]: # ({current_id})'
                    in_message = False

                if not is_first_message:
                    yield '\n\n'
                is_first_message = False

                current_intent = item
                current_id = _new_id()
                in_message = True

                open_comment = f'[//]: # ({current_intent}: {current_id})'
                yield f'{open_comment}\n\n'

                if current_intent not in [ChatIntent.RESPONSE, ChatIntent.STATUS]:
                    yield f'<details>\n<summary>{current_intent}</summary>\n\n'

            elif isinstance(item, str) and item:
                yield item

        if in_message:
            yield '\n\n'
            if current_intent and current_intent not in [ChatIntent.RESPONSE, ChatIntent.STATUS]:
                yield '</details>\n\n'
            yield f'[//]: # ({current_id})'

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
        i = 0
        while i < len(lines):
            line = lines[i]
            match = _OPEN_RE.fullmatch(line)
            if match:
                intent_str, msg_id = match.groups()
                try:
                    intent = ChatIntent.parse(intent_str)
                    start_content = i + 1
                    # Look for closing tag
                    close_comment = f'[//]: # ({msg_id})'
                    found_close = False
                    while i < len(lines):
                        if lines[i] == close_comment:
                            found_close = True
                            break
                        i += 1

                    if found_close:
                        content_lines = lines[start_content:i]
                        # strip at most one empty line from start and end
                        if content_lines and not content_lines[0]:
                            content_lines = content_lines[1:]
                        if content_lines and not content_lines[-1]:
                            content_lines = content_lines[:-1]

                        if intent not in [ChatIntent.RESPONSE, ChatIntent.STATUS]:
                            if (len(content_lines) >= 4 and
                                content_lines[0].strip() == '<details>' and
                                content_lines[-1].strip() == '</details>' and
                                content_lines[1].strip().startswith('<summary>')):

                                if len(content_lines) == 4 and not content_lines[2].strip():
                                    content_lines = []
                                elif (len(content_lines) >= 6 and
                                      not content_lines[2].strip() and
                                      not content_lines[-2].strip()):
                                    content_lines = content_lines[3:-2]

                        content = '\n'.join(content_lines)
                        builder.add(ChatMessage(intent, content))
                except ValueError:
                    # Not a valid intent, ignore.
                    pass
            i += 1
        return builder.build()

__all__ = [
    'LinkCommentSubmessageFormat',
]
