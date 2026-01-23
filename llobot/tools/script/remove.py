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
from llobot.tools.script import ScriptItem

class ScriptRemove(ScriptItem):
    """
    Tool that parses `rm ~/path` commands.
    """
    def execute(self, env: Environment, line: str) -> bool:
        try:
            parts = shlex.split(line)
        except ValueError:
            return False

        if len(parts) != 2 or parts[0] != 'rm':
            return False

        path_str = parts[1]
        path = parse_path(path_str)

        project = env[ProjectEnv].union
        project.remove(path)
        env[ContextEnv].add(ChatMessage(ChatIntent.STATUS, f"Removed `~/{path}`"))
        return True

__all__ = [
    'ScriptRemove',
]
