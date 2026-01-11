"""
Tool for writing files from document listings.
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
from llobot.tools.block import BlockTool
from llobot.utils.text import normalize_document

class WriteToolCall(ToolCall):
    _path: str
    _content: str
    _fence_length: int | None

    def __init__(self, path: str, content: str, fence_length: int | None = None):
        self._path = path
        self._content = content
        self._fence_length = fence_length

    @property
    def title(self) -> str:
        return f"write {self._path}"

    def execute(self, env: Environment):
        path = parse_path(self._path)
        project = env[ProjectEnv].union

        if self._fence_length is not None:
            if re.search(r'^`{%d,}' % self._fence_length, self._content, re.MULTILINE):
                raise ValueError(f"Content contains a line starting with {self._fence_length} or more backticks. Enclose the block in more backticks.")

        project.write(path, normalize_document(self._content))
        env[ContextEnv].add(ChatMessage(ChatIntent.STATUS, f"Written ~/{path}"))

_WRITE_DETAILS_RE = re.compile(
    r'^<details>\s*<summary>\s*Write:\s*(?P<path>.+?)\s*</summary>\s*'
    r'^(?P<fence>`{3,})(?P<lang>[^`\n]*)\s*\n'
    r'(?P<content>.*?)'
    r'^(?P=fence)\s*</details>',
    re.DOTALL | re.MULTILINE
)


class WriteTool(BlockTool):
    """
    Tool that parses document listings in the format:
    <details>
    <summary>Write: ~/path/to/file</summary>

    ```lang
    content
    ```

    </details>
    """
    def slice(self, env: Environment, source: str, at: int) -> int:
        match = _WRITE_DETAILS_RE.match(source, pos=at)
        if not match:
            return 0
        return match.end() - at

    def parse(self, env: Environment, source: str) -> Iterable[ToolCall]:
        match = _WRITE_DETAILS_RE.fullmatch(source)
        assert match, "source for parse() must be validated by slice()"

        path_str = match.group('path').strip()
        fence = match.group('fence')
        content = match.group('content')

        yield WriteToolCall(path_str, content, len(fence))

__all__ = [
    'WriteTool',
    'WriteToolCall',
]
