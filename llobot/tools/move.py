"""
Tool for moving files.
"""
from __future__ import annotations
from pathlib import Path
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
    _source: Path
    _destination: Path

    def __init__(self, source: Path, destination: Path):
        self._source = source
        self._destination = destination

    @property
    def title(self) -> str:
        return f"mv {self._source} {self._destination}"

    def execute(self, env: Environment):
        project = env[ProjectEnv].union
        if project.read(self._destination) is not None:
            env[ToolEnv].log(f"Warning: Overwriting {self._destination}")
        env[ToolEnv].log(f"Moving {self._source} to {self._destination}...")
        project.move(self._source, self._destination)
        env[ToolEnv].log("File was moved.")

class MoveTool(FencedTool):
    """
    Tool that parses `mv source dest` commands inside `tool` code blocks.
    """
    def __init__(self):
        super().__init__()

    def matches_content(self, source: str) -> bool:
        return _MV_COMMAND_RE.fullmatch(source) is not None

    def parse_content(self, source: str) -> ToolCall:
        match = _MV_COMMAND_RE.fullmatch(source)
        assert match, "source for parse_content() must be valid"
        return MoveToolCall(Path(match.group(1)), Path(match.group(2)))

__all__ = [
    'MoveTool',
    'MoveToolCall',
]
