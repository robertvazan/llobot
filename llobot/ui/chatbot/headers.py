from __future__ import annotations
from datetime import datetime
import re
import llobot.ui.chatbot.commands
from llobot.ui.chatbot.commands import ChatbotCommand
import llobot.time
import llobot.models.streams

class ChatbotHeader:
    _project: str | None
    _cutoff: datetime | None
    _command: ChatbotCommand | None
    _model: str | None
    _options: dict | None

    def __init__(self, *,
        project: str | None = None,
        cutoff: datetime | None = None,
        command: ChatbotCommand | None = None,
        model: str | None = None,
        options: dict | None = None
    ):
        self._project = project
        self._cutoff = cutoff
        self._command = command
        self._model = model
        self._options = options

    @property
    def project(self) -> str | None:
        return self._project
    
    @property
    def cutoff(self) -> datetime | None:
        return self._cutoff
    
    @property
    def command(self) -> ChatbotCommand | None:
        return self._command
    
    @property
    def model(self) -> str | None:
        return self._model
    
    @property
    def options(self) -> dict | None:
        return self._options

HEADER_RE = re.compile(r'(?:~([a-zA-Z0-9_/.-]+))?(?::([0-9-]+))?(?:@([a-zA-Z0-9:/._-]+))?(?:\?([^!\s]+))?(?:!([a-z]+))?')

def parse_options(query: str) -> dict:
    options = {}
    for pair in query.split('&'):
        if '=' not in pair:
            llobot.models.streams.fail(f'Invalid model option: {pair}')
        key, value = pair.split('=', maxsplit=1)
        options[key] = value if value else None
    return options

def parse_line(line: str) -> ChatbotHeader | None:
    if not line:
        return None
    m = HEADER_RE.fullmatch(line.strip())
    if not m:
        return None
    
    project = m[1] if m[1] else None
    cutoff = llobot.time.parse(m[2]) if m[2] else None
    model = m[3] if m[3] else None
    options = parse_options(m[4]) if m[4] else None
    command = llobot.ui.chatbot.commands.decode(m[5]) if m[5] else None
    return ChatbotHeader(project=project, cutoff=cutoff, command=command, model=model, options=options)

def parse(message: str) -> ChatbotHeader | None:
    lines = message.strip().splitlines()
    header = None
    if lines:
        top = parse_line(lines[0])
        bottom = parse_line(lines[-1]) if len(lines) > 1 else None
        if top and bottom:
            llobot.models.streams.fail('Command header is both at the top and bottom of the message.')
        header = top or bottom
    return header

def strip(message: str) -> str:
    lines = message.strip().splitlines()
    if lines and parse_line(lines[0]):
        lines = lines[1:]
    if lines and parse_line(lines[-1]):
        lines = lines[:-1]
    return '\n'.join(lines).strip()

__all__ = [
    'ChatbotHeader',
    'parse_options',
    'parse_line',
    'parse',
    'strip',
]
