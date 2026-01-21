"""
Tool for executing shell scripts.
"""
from __future__ import annotations
import shlex
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

    def __init__(self, script: str):
        self._script = script

    @property
    def title(self) -> str:
        return "shell script"

    def execute(self, env: Environment):
        project = env[ProjectEnv].union
        path = self._determine_path(project, self._script)

        output = project.execute(path, self._script)

        formatted = markdown_code_details("Shell tool output", "", output)
        env[ContextEnv].add(ChatMessage(ChatIntent.STATUS, formatted))

    def _determine_path(self, project: Project, script: str) -> PurePosixPath:
        # Check for explicit cd command
        for line in script.splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            try:
                tokens = shlex.split(line, comments=True)
            except ValueError:
                # Malformed shell syntax (e.g. unbalanced quotes)
                break

            if tokens and tokens[0] == 'cd':
                if len(tokens) < 2:
                    raise ValueError("Shell script 'cd' command missing path argument.")

                path_str = tokens[1]
                if path_str.startswith('~/'):
                    return parse_path(path_str)
                else:
                    raise ValueError("Shell script must start with 'cd ~/path' to specify execution directory.")

            # First non-empty non-comment line is not cd
            break

        # Fallback to default executable prefix
        executable_prefixes = [p for p in project.prefixes if project.executable(p)]
        if len(executable_prefixes) == 1:
            return executable_prefixes[0]

        if len(executable_prefixes) == 0:
            raise ValueError("No path specified in script (cd ~/path) and no executable projects found.")

        formatted_prefixes = [f"~/{p}" for p in executable_prefixes]
        raise ValueError(f"No path specified in script (cd ~/path) and multiple executable projects found: {formatted_prefixes}")

class ShellTool(FencedTool):
    """
    A tool that executes shell scripts within a fenced code block.
    """
    def __init__(self):
        super().__init__(language='shelltool')

    def matches_content(self, env: Environment, source: str) -> bool:
        return True

    def parse_content(self, env: Environment, source: str) -> Iterable[ToolCall]:
        yield ShellToolCall(source)

__all__ = [
    'ShellTool',
]
