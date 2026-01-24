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
from llobot.tools.script import ScriptItem

class ScriptMove(ScriptItem):
    """
    Tool that parses `mv ~/source ~/dest` commands.
    """
    def execute(self, env: Environment, line: str) -> bool:
        try:
            parts = shlex.split(line)
        except ValueError:
            return False

        if len(parts) != 3 or parts[0] != 'mv':
            return False

        source_path = parts[1]
        dest_path = parts[2]

        source = parse_path(source_path)
        destination = parse_path(dest_path)

        context_env = env[ContextEnv]
        project = env[ProjectEnv].union

        msg = f"✅ Moved `~/{source}` to `~/{destination}`"
        if project.read(destination) is not None:
            msg += f" (overwriting `~/{destination}`)"

        project.move(source, destination)
        context_env.add(ChatMessage(ChatIntent.STATUS, msg))
        return True

__all__ = [
    'ScriptMove',
]
