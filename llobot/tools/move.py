"""
Tool for moving files.
"""
from __future__ import annotations
from pathlib import PurePosixPath
import shlex
from llobot.environments import Environment
from llobot.environments.projects import ProjectEnv
from llobot.environments.tools import ToolEnv
from llobot.formats.paths import parse_path
from llobot.tools import ToolCall
from llobot.tools.fenced import FencedTool

class MoveToolCall(ToolCall):
    """
    A tool call for moving a file.
    """
    _source: PurePosixPath
    _destination: PurePosixPath

    def __init__(self, source: PurePosixPath, destination: PurePosixPath):
        self._source = source
        self._destination = destination

    @property
    def title(self) -> str:
        return f"mv ~/{self._source} ~/{self._destination}"

    def execute(self, env: Environment):
        project = env[ProjectEnv].union
        if project.read(self._destination) is not None:
            env[ToolEnv].log(f"Warning: Overwriting ~/{self._destination}")
        env[ToolEnv].log(f"Moving ~/{self._source} to ~/{self._destination}...")
        project.move(self._source, self._destination)
        env[ToolEnv].log("File was moved.")

class MoveTool(FencedTool):
    """
    Tool that parses `mv ~/source ~/dest` commands inside `tool` code blocks.
    """
    def __init__(self):
        super().__init__()

    def matches_content(self, env: Environment, source: str) -> bool:
        if '\n' in source or '\r' in source:
            return False
        try:
            parts = shlex.split(source)
        except ValueError:
            return False
        return len(parts) == 3 and parts[0] == 'mv'

    def parse_content(self, env: Environment, source: str) -> ToolCall:
        if '\n' in source or '\r' in source:
            raise ValueError("mv command must be single-line (raw newline is not allowed)")
        parts = shlex.split(source)
        # matches_content checks structure, but let's be safe
        if len(parts) != 3 or parts[0] != 'mv':
            raise ValueError(f"Invalid mv command: {source}")

        source_path = parse_path(parts[1])
        dest_path = parse_path(parts[2])

        return MoveToolCall(source_path, dest_path)

__all__ = [
    'MoveTool',
    'MoveToolCall',
]
