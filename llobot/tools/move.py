"""
Tool for moving files.
"""
from __future__ import annotations
from pathlib import PurePosixPath
import re
from llobot.environments import Environment
from llobot.environments.projects import ProjectEnv
from llobot.environments.tools import ToolEnv
from llobot.tools import ToolCall
from llobot.tools.fenced import FencedTool

_MV_COMMAND_RE = re.compile(r'^\s*mv\s+([^\s]+)\s+([^\s]+)\s*$')

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

    def matches_content(self, source: str) -> bool:
        return _MV_COMMAND_RE.fullmatch(source) is not None

    def parse_content(self, source: str) -> ToolCall:
        match = _MV_COMMAND_RE.fullmatch(source)
        assert match, "source for parse_content() must be valid"
        source_str = match.group(1)
        dest_str = match.group(2)

        if not source_str.startswith('~/'):
            raise ValueError(f"Source path must start with ~/: {source_str}")
        if not dest_str.startswith('~/'):
            raise ValueError(f"Destination path must start with ~/: {dest_str}")

        source_path = PurePosixPath(source_str[2:])
        dest_path = PurePosixPath(dest_str[2:])

        if source_path.is_absolute():
            raise ValueError(f"Internal source path must be relative: {source_path}")
        if dest_path.is_absolute():
            raise ValueError(f"Internal destination path must be relative: {dest_path}")

        return MoveToolCall(source_path, dest_path)

__all__ = [
    'MoveTool',
    'MoveToolCall',
]
