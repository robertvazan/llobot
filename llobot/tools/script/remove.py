"""
Script item for removing files.
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

class ScriptRemoveCall(ToolCall):
    """
    A tool call for removing a file.
    """
    _path: str

    def __init__(self, path: str):
        self._path = path

    @property
    def summary(self) -> str:
        return f"rm `{self._path}`"

    def execute(self, env: Environment):
        path = parse_path(self._path)
        project = env[ProjectEnv].union
        project.remove(path)
        env[ContextEnv].add(ChatMessage(ChatIntent.STATUS, f"Removed `~/{path}`"))

class ScriptRemove(ScriptItem):
    """
    Tool that parses `rm ~/path` commands.
    """
    def matches(self, env: Environment, line: str) -> bool:
        try:
            parts = shlex.split(line)
        except ValueError:
            return False
        return len(parts) == 2 and parts[0] == 'rm'

    def parse(self, env: Environment, line: str) -> ToolCall:
        parts = shlex.split(line)
        # matches checks structure, but let's be safe
        if len(parts) != 2 or parts[0] != 'rm':
            raise ValueError(f"Invalid rm command: {line}")

        path = parts[1]

        return ScriptRemoveCall(path)

__all__ = [
    'ScriptRemove',
    'ScriptRemoveCall',
]
