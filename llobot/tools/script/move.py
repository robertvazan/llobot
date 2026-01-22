"""
Script item for moving files.
"""
from __future__ import annotations
import shlex
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.projects import ProjectEnv
from llobot.formats.paths import parse_path
from llobot.tools import ToolCall
from llobot.tools.script import ScriptItem

class ScriptMoveCall(ToolCall):
    """
    A tool call for moving a file.
    """
    _source: str
    _destination: str

    def __init__(self, source: str, destination: str):
        self._source = source
        self._destination = destination

    @property
    def summary(self) -> str:
        return f"mv `{self._source}` `{self._destination}`"

    def execute(self, env: Environment):
        source = parse_path(self._source)
        destination = parse_path(self._destination)

        context_env = env[ContextEnv]
        project = env[ProjectEnv].union

        msg = f"Moved `~/{source}` to `~/{destination}`"
        if project.read(destination) is not None:
            msg += f" (overwriting `~/{destination}`)"

        project.move(source, destination)
        context_env.add(ChatMessage(ChatIntent.STATUS, msg))

class ScriptMove(ScriptItem):
    """
    Tool that parses `mv ~/source ~/dest` commands.
    """
    def matches(self, env: Environment, line: str) -> bool:
        try:
            parts = shlex.split(line)
        except ValueError:
            return False
        return len(parts) == 3 and parts[0] == 'mv'

    def parse(self, env: Environment, line: str) -> ToolCall:
        parts = shlex.split(line)
        # matches checks structure, but let's be safe
        if len(parts) != 3 or parts[0] != 'mv':
            raise ValueError(f"Invalid mv command: {line}")

        source_path = parts[1]
        dest_path = parts[2]

        return ScriptMoveCall(source_path, dest_path)

__all__ = [
    'ScriptMove',
    'ScriptMoveCall',
]
