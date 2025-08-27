from __future__ import annotations
from enum import Enum
import re

class ChatbotCommand(Enum):
    OK = 'ok'
    ECHO = 'echo'

COMMAND_RE = re.compile(r'!([a-z]+)')

def decode(name: str) -> ChatbotCommand:
    for command in ChatbotCommand:
        if command.value == name:
            return command
    raise ValueError(f'Invalid command: {name}')

def parse_line(line: str) -> ChatbotCommand | None:
    m = COMMAND_RE.fullmatch(line.strip())
    return decode(m[1]) if m else None

def parse(message: str) -> ChatbotCommand | None:
    lines = message.strip().splitlines()
    if not lines:
        return None
    top = parse_line(lines[0])
    bottom = parse_line(lines[-1]) if len(lines) > 1 else None
    if top and bottom:
        raise ValueError('Command is both at the top and bottom of the message.')
    return top or bottom

def strip(message: str) -> str:
    lines = message.strip().splitlines()
    if lines and parse_line(lines[0]):
        lines = lines[1:]
    if lines and parse_line(lines[-1]):
        lines = lines[:-1]
    return '\n'.join(lines).strip()

__all__ = [
    'ChatbotCommand',
    'decode',
    'parse_line',
    'parse',
    'strip',
]
