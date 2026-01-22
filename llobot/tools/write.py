"""
Tool for writing files from document listings.
"""
from __future__ import annotations
from typing import Iterable
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.projects import ProjectEnv
from llobot.formats.paths import parse_path
from llobot.tools import ToolCall
from llobot.tools.fenced import FencedTool
from llobot.utils.text import normalize_document

class WriteToolCall(ToolCall):
    _path: str
    _content: str

    def __init__(self, path: str, content: str):
        self._path = path
        self._content = content

    @property
    def summary(self) -> str:
        return f"write: {self._path}"

    def execute(self, env: Environment):
        path = parse_path(self._path)
        project = env[ProjectEnv].union

        project.write(path, normalize_document(self._content))
        env[ContextEnv].add(ChatMessage(ChatIntent.STATUS, f"Written `~/{path}`"))


class WriteTool(FencedTool):
    """
    Tool that parses document listings in the format:
    <details>
    <summary>write: ~/path/to/file</summary>

    ```lang
    content
    ```

    </details>
    """
    def matches_content(self, env: Environment, name: str, header: str, content: str) -> bool:
        return name == 'write'

    def parse_content(self, env: Environment, name: str, header: str, content: str) -> Iterable[ToolCall]:
        yield WriteToolCall(header, content)

__all__ = [
    'WriteTool',
    'WriteToolCall',
]
