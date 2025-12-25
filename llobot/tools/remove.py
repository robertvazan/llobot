"""
Tool for removing files.
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

class RemoveToolCall(ToolCall):
    """
    A tool call for removing a file.
    """
    _path: PurePosixPath

    def __init__(self, path: PurePosixPath):
        self._path = path

    @property
    def title(self) -> str:
        return f"rm ~/{self._path}"

    def execute(self, env: Environment):
        project = env[ProjectEnv].union
        env[ToolEnv].log(f"Removing ~/{self._path}...")
        project.remove(self._path)
        env[ToolEnv].log("File was removed.")

class RemoveTool(FencedTool):
    """
    Tool that parses `rm ~/path` commands inside `tool` code blocks.
    """
    def __init__(self):
        super().__init__()

    def matches_content(self, source: str) -> bool:
        if '\n' in source or '\r' in source:
            return False
        try:
            parts = shlex.split(source)
        except ValueError:
            return False
        return len(parts) == 2 and parts[0] == 'rm'

    def parse_content(self, source: str) -> ToolCall:
        if '\n' in source or '\r' in source:
            raise ValueError("rm command must be single-line (raw newline is not allowed)")
        parts = shlex.split(source)
        # matches_content checks structure, but let's be safe
        if len(parts) != 2 or parts[0] != 'rm':
            raise ValueError(f"Invalid rm command: {source}")

        path = parse_path(parts[1])

        return RemoveToolCall(path)

__all__ = [
    'RemoveTool',
    'RemoveToolCall',
]
