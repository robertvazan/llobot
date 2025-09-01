import re
from pathlib import Path
from llobot.chats import ChatIntent, ChatBranch, ChatBuilder, ChatMessage
import llobot.fs

SUFFIX = '.md'

_INTENT_RE = re.compile('> ([A-Z][-A-Za-z]*)')

def format(chat: ChatBranch) -> str:
    lines = []
    for message in chat:
        lines.append('')
        lines.append(f'> {message.intent}')
        lines.append('')
        for line in message.content.splitlines():
            matched = _INTENT_RE.fullmatch(line)
            if matched:
                lines.append(f'> Escaped-{matched.group(1)}')
            else:
                lines.append(line)
        if message.content.endswith('\n'):
            lines.append('')
    # Remove leading blank line if present
    if lines and not lines[0]:
        lines.pop(0)
    return ''.join([l + '\n' for l in lines])

def parse(formatted: str) -> ChatBranch:
    builder = ChatBuilder()
    intent = None
    lines = None
    first_message = True
    for line in formatted.splitlines():
        # Empty line before first message.
        if first_message and not intent and not line:
            continue
        matched = _INTENT_RE.fullmatch(line)
        if matched:
            if matched.group(1).startswith('Escaped-'):
                if not intent:
                    raise ValueError
                lines.append('> ' + matched.group(1).removeprefix('Escaped-'))
            else:
                if intent:
                    if len(lines) < 2 or lines[0] or lines[-1]:
                        raise ValueError
                    builder.add(ChatMessage(intent, '\n'.join(lines[1:-1])))
                intent = ChatIntent.parse(matched.group(1))
                lines = []
                first_message = False
        else:
            if not intent:
                # Tolerate content before first intent, for example old metadata format.
                continue
            lines.append(line)
    if intent:
        if len(lines) < 1 or lines[0]:
            raise ValueError
        builder.add(ChatMessage(intent, '\n'.join(lines[1:])))
    return builder.build()

def save(path: Path, chat: ChatBranch):
    llobot.fs.write_text(path, format(chat))

def load(path: Path) -> ChatBranch:
    return parse(llobot.fs.read_text(path))

__all__ = [
    'SUFFIX',
    'format',
    'parse',
    'save',
    'load',
]
