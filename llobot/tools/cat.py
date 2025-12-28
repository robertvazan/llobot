"""
Tool for reading files.
"""
from __future__ import annotations
from pathlib import PurePosixPath
import shlex
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.projects import ProjectEnv
from llobot.environments.tools import ToolEnv
from llobot.formats.documents import DocumentFormat, standard_document_format
from llobot.formats.paths import parse_path
from llobot.tools import ToolCall
from llobot.tools.line import LineTool

class CatToolCall(ToolCall):
    """
    A tool call for reading a file.
    """
    _path: PurePosixPath
    _format: DocumentFormat

    def __init__(self, path: PurePosixPath, format: DocumentFormat):
        self._path = path
        self._format = format

    @property
    def title(self) -> str:
        return f"cat ~/{self._path}"

    def execute(self, env: Environment):
        project = env[ProjectEnv].union
        env[ToolEnv].log(f"Reading ~/{self._path}...")
        content = project.read(self._path)
        if content is None:
            raise ValueError(f"File not found: ~/{self._path}")

        listing = self._format.render(self._path, content)

        # Deduplicate output if file is already in context.
        context = env[ContextEnv].build()
        if any(listing in msg.content for msg in context):
            env[ToolEnv].log("File is already in the context.")
            return

        env[ToolEnv].output(listing)
        env[ToolEnv].log("File was read.")

class CatTool(LineTool):
    """
    Tool that parses `cat ~/path` commands.
    """
    _format: DocumentFormat

    def __init__(self, format: DocumentFormat | None = None):
        """
        Initializes a new CatTool.

        Args:
            format: The document format to use for output. Defaults to standard format.
        """
        self._format = format or standard_document_format()

    def matches_line(self, env: Environment, line: str) -> bool:
        try:
            parts = shlex.split(line)
        except ValueError:
            return False
        return len(parts) == 2 and parts[0] == 'cat'

    def parse_line(self, env: Environment, line: str) -> ToolCall:
        parts = shlex.split(line)
        # matches_line checks structure, but let's be safe
        if len(parts) != 2 or parts[0] != 'cat':
            raise ValueError(f"Invalid cat command: {line}")

        path = parse_path(parts[1])

        return CatToolCall(path, self._format)

__all__ = [
    'CatTool',
    'CatToolCall',
]
