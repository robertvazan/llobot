import re
from pathlib import Path
from llobot.chats import ChatIntent, ChatMetadata, ChatBranch, ChatBuilder
import llobot.fs
import llobot.chats.json

SUFFIX = '.md'

def format_intent(intent: ChatIntent) -> str:
    if intent == ChatIntent.SYSTEM:
        return 'System'
    if intent == ChatIntent.AFFIRMATION:
        return 'Affirmation'
    if intent == ChatIntent.EXAMPLE_PROMPT:
        return 'Example-Prompt'
    if intent == ChatIntent.EXAMPLE_RESPONSE:
        return 'Example-Response'
    if intent == ChatIntent.PROMPT:
        return 'Prompt'
    if intent == ChatIntent.RESPONSE:
        return 'Response'
    raise ValueError

def parse_intent(codename: str) -> ChatIntent:
    if codename == 'System' or codename == 'Context':
        return ChatIntent.SYSTEM
    if codename == 'Affirmation':
        return ChatIntent.AFFIRMATION
    if codename == 'Example-Prompt':
        return ChatIntent.EXAMPLE_PROMPT
    if codename == 'Example-Response':
        return ChatIntent.EXAMPLE_RESPONSE
    if codename == 'Prompt':
        return ChatIntent.PROMPT
    if codename == 'Response':
        return ChatIntent.RESPONSE
    raise ValueError(f'Unknown intent: {codename}')

_INTENT_RE = re.compile('> ([A-Z][-A-Za-z]*)')

def format(chat: ChatBranch) -> str:
    lines = []
    if chat.metadata:
        lines.append(f'Metadata: `{llobot.chats.json.format_metadata(chat.metadata)}`')
    for message in chat:
        lines.append('')
        lines.append(f'> {format_intent(message.intent)}')
        lines.append('')
        for line in message.content.splitlines():
            matched = _INTENT_RE.fullmatch(line)
            if matched:
                lines.append(f'> Escaped-{matched.group(1)}')
            else:
                lines.append(line)
        if message.content.endswith('\n'):
            lines.append('')
    return ''.join([l + '\n' for l in lines])

def parse(formatted: str) -> ChatBranch:
    metadata = ChatMetadata()
    builder = ChatBuilder()
    intent = None
    lines = None
    for line in formatted.splitlines():
        if not metadata and not intent:
            matched = re.fullmatch('Metadata: `(.*)`', line)
            if matched:
                metadata = llobot.chats.json.parse_metadata(matched.group(1))
                continue
        # Empty line after metadata.
        if not intent and not line:
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
                    builder.add(intent.message('\n'.join(lines[1:-1])))
                intent = parse_intent(matched.group(1))
                lines = []
        else:
            if not intent:
                raise ValueError
            lines.append(line)
    if intent:
        if len(lines) < 1 or lines[0]:
            raise ValueError
        builder.add(intent.message('\n'.join(lines[1:])))
    return builder.build().with_metadata(metadata)

def save(path: Path, chat: ChatBranch):
    llobot.fs.write_text(path, format(chat))
    
def load(path: Path) -> ChatBranch:
    return parse(llobot.fs.read_text(path))

__all__ = [
    'SUFFIX',
    'format_intent',
    'parse_intent',
    'format',
    'parse',
    'save',
    'load',
]

