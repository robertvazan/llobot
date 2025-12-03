"""
Tool for removing files.
"""
from __future__ import annotations
from pathlib import Path
import re
from llobot.environments import Environment
from llobot.environments.projects import ProjectEnv
from llobot.environments.tools import ToolEnv
from llobot.tools import ToolCall
from llobot.tools.fenced import FencedTool

_RM_COMMAND_RE = re.compile(r'^\s*rm\s+([^\s]+)\s*$')

class RemoveToolCall(ToolCall):
    """
    A tool call for removing a file.
    """
    _path: Path

    def __init__(self, path: Path):
        self._path = path

    @property
    def title(self) -> str:
        return f"rm {self._path}"

    def execute(self, env: Environment):
        project = env[ProjectEnv].union
        env[ToolEnv].log(f"Removing {self._path}...")
        project.remove(self._path)
        env[ToolEnv].log("File was removed.")

class RemoveTool(FencedTool):
    """
    Tool that parses `rm path` commands inside `tool` code blocks.
    """
    def __init__(self):
        super().__init__()

    def matches_content(self, source: str) -> bool:
        return _RM_COMMAND_RE.fullmatch(source) is not None

    def parse_content(self, source: str) -> ToolCall:
        match = _RM_COMMAND_RE.fullmatch(source)
        assert match, "source for parse_content() must be valid"
        return RemoveToolCall(Path(match.group(1)))

__all__ = [
    'RemoveTool',
    'RemoveToolCall',
]
