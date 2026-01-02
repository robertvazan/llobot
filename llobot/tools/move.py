"""
Tool for moving files.
"""
from __future__ import annotations
import shlex
from llobot.environments import Environment
from llobot.environments.projects import ProjectEnv
from llobot.environments.tools import ToolEnv
from llobot.formats.paths import parse_path
from llobot.tools import ToolCall
from llobot.tools.line import LineTool

class MoveToolCall(ToolCall):
    """
    A tool call for moving a file.
    """
    _source: str
    _destination: str

    def __init__(self, source: str, destination: str):
        self._source = source
        self._destination = destination

    @property
    def title(self) -> str:
        return f"mv {self._source} {self._destination}"

    def execute(self, env: Environment):
        source = parse_path(self._source)
        destination = parse_path(self._destination)

        project = env[ProjectEnv].union
        if project.read(destination) is not None:
            env[ToolEnv].log(f"Warning: Overwriting ~/{destination}")
        project.move(source, destination)

class MoveTool(LineTool):
    """
    Tool that parses `mv ~/source ~/dest` commands.
    """
    def matches_line(self, env: Environment, line: str) -> bool:
        try:
            parts = shlex.split(line)
        except ValueError:
            return False
        return len(parts) == 3 and parts[0] == 'mv'

    def parse_line(self, env: Environment, line: str) -> ToolCall:
        parts = shlex.split(line)
        # matches_line checks structure, but let's be safe
        if len(parts) != 3 or parts[0] != 'mv':
            raise ValueError(f"Invalid mv command: {line}")

        source_path = parts[1]
        dest_path = parts[2]

        return MoveToolCall(source_path, dest_path)

__all__ = [
    'MoveTool',
    'MoveToolCall',
]
