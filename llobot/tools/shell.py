"""
Tool for executing shell scripts.
"""
from __future__ import annotations
import re
from pathlib import PurePosixPath
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.projects import ProjectEnv
from llobot.formats.paths import parse_path
from llobot.projects import Project
from llobot.tools.fenced import FencedTool
from llobot.utils.text import markdown_code_details

_SHELL_HEADER_RE = re.compile(r'^(?P<description>.*)\s+@\s+(?P<path>~/.+)$')

class ShellTool(FencedTool):
    """
    A tool that executes shell scripts within a fenced code block.
    """
    def match_fenced(self, env: Environment, name: str, header: str, content: str) -> bool:
        return name == 'Shell'

    def execute_fenced(self, env: Environment, name: str, header: str, content: str) -> bool:
        match = _SHELL_HEADER_RE.match(header)
        if match:
            description = match.group('description').strip()
            path_str = match.group('path').strip()
        else:
            description = header
            path_str = None

        script = content

        project = env[ProjectEnv].union
        path = self._determine_path(project, path_str)

        output = project.execute(path, script)

        # Always include path in summary
        result_header = f"{description} @ ~/{path}"
        formatted = markdown_code_details(f"Shell output: {result_header}", "", output)
        env[ContextEnv].add(ChatMessage(ChatIntent.STATUS, formatted))
        return True

    def _determine_path(self, project: Project, path_str: str | None) -> PurePosixPath:
        if path_str:
            return parse_path(path_str)

        # Fallback to default executable prefix
        executable_prefixes = [p for p in project.prefixes if project.executable(p)]
        if len(executable_prefixes) == 1:
            return executable_prefixes[0]

        if len(executable_prefixes) == 0:
            raise ValueError("No path specified in shell header (Shell: desc @ ~/path) and no executable projects found.")

        formatted_prefixes = [f"~/{p}" for p in executable_prefixes]
        raise ValueError(f"No path specified in shell header (Shell: desc @ ~/path) and multiple executable projects found: {formatted_prefixes}")

__all__ = [
    'ShellTool',
]
