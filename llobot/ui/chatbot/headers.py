from __future__ import annotations
import re

class ChatbotHeader:
    _project: str | None

    def __init__(self, *,
        project: str | None = None,
    ):
        self._project = project

    @property
    def project(self) -> str | None:
        return self._project

HEADER_RE = re.compile(r'~([a-zA-Z0-9_/.-]+)')

def parse_line(line: str) -> ChatbotHeader | None:
    if not line:
        return None
    m = HEADER_RE.fullmatch(line.strip())
    if not m:
        return None
    project = m[1] or None
    return ChatbotHeader(project=project)

def parse(message: str) -> ChatbotHeader | None:
    lines = message.strip().splitlines()
    header = None
    if lines:
        top = parse_line(lines[0])
        bottom = parse_line(lines[-1]) if len(lines) > 1 else None
        if top and bottom:
            raise ValueError('Command header is both at the top and bottom of the message.')
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
    'parse_line',
    'parse',
    'strip',
]
