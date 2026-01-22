"""
Tool for executing shell scripts.
"""
from __future__ import annotations
import re
from typing import Iterable
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.projects import ProjectEnv
from llobot.formats.paths import parse_path
from llobot.tools import ToolCall
from llobot.tools.fenced import FencedTool
from llobot.utils.text import markdown_code_details
from pathlib import PurePosixPath
from llobot.projects import Project

class ShellToolCall(ToolCall):
    """
    A tool call to execute a shell script.
    """
    _script: str
    _path_str: str | None
    _description: str

    def __init__(self, script: str, path: str | None, description: str):
        self._script = script
        self._path_str = path
        self._description = description

    @property
    def summary(self) -> str:
        if self._path_str:
             return f"shell: {self._description} @ {self._path_str}"
        return f"shell: {self._description}"

    def execute(self, env: Environment):
        project = env[ProjectEnv].union
        path = self._determine_path(project)

        output = project.execute(path, self._script)

        # Always include path in summary
        header = f"{self._description} @ ~/{path}"
        formatted = markdown_code_details(f"Shell output: {header}", "", output)
        env[ContextEnv].add(ChatMessage(ChatIntent.STATUS, formatted))

    def _determine_path(self, project: Project) -> PurePosixPath:
        if self._path_str:
            return parse_path(self._path_str)

        # Fallback to default executable prefix
        executable_prefixes = [p for p in project.prefixes if project.executable(p)]
        if len(executable_prefixes) == 1:
            return executable_prefixes[0]

        if len(executable_prefixes) == 0:
            raise ValueError("No path specified in shell header (shell: desc @ ~/path) and no executable projects found.")

        formatted_prefixes = [f"~/{p}" for p in executable_prefixes]
        raise ValueError(f"No path specified in shell header (shell: desc @ ~/path) and multiple executable projects found: {formatted_prefixes}")

_SHELL_HEADER_RE = re.compile(r'^(?P<description>.*)\s+@\s+(?P<path>~/.+)$')

class ShellTool(FencedTool):
    """
    A tool that executes shell scripts within a fenced code block.
    """
    def matches_content(self, env: Environment, name: str, header: str, content: str) -> bool:
        return name == 'shell'

    def parse_content(self, env: Environment, name: str, header: str, content: str) -> Iterable[ToolCall]:
        match = _SHELL_HEADER_RE.match(header)
        if match:
            description = match.group('description').strip()
            path_str = match.group('path').strip()
        else:
            description = header
            path_str = None

        yield ShellToolCall(content, path=path_str, description=description)

__all__ = [
    'ShellTool',
]
