"""
Tool for writing files from document listings.
"""
from __future__ import annotations
from pathlib import PurePosixPath
import re
from llobot.environments import Environment
from llobot.environments.projects import ProjectEnv
from llobot.environments.tools import ToolEnv
from llobot.formats.paths import parse_path
from llobot.tools import Tool, ToolCall
from llobot.utils.text import normalize_document

class FileToolCall(ToolCall):
    _path: PurePosixPath
    _content: str

    def __init__(self, path: PurePosixPath, content: str):
        self._path = path
        self._content = content

    @property
    def title(self) -> str:
        return f"file ~/{self._path}"

    def execute(self, env: Environment):
        project = env[ProjectEnv].union
        env[ToolEnv].log(f"Writing ~/{self._path}...")
        project.write(self._path, normalize_document(self._content))
        env[ToolEnv].log("File was written.")

_FILE_DETAILS_RE = re.compile(
    r'^<details>\s*<summary>\s*File:\s*(?P<path>.+?)\s*</summary>\s*'
    r'^(?P<fence>`{3,})(?P<lang>\w*)\s*\n'
    r'(?P<content>.*?)'
    r'^(?P=fence)\s*</details>',
    re.DOTALL | re.MULTILINE
)


class FileTool(Tool):
    """
    Tool that parses document listings in the format:
    <details>
    <summary>File: ~/path/to/file</summary>

    ```lang
    content
    ```

    </details>
    """
    def slice(self, source: str, at: int) -> int:
        match = _FILE_DETAILS_RE.match(source, pos=at)
        if not match:
            return 0
        return match.end() - at

    def parse(self, source: str) -> ToolCall:
        match = _FILE_DETAILS_RE.fullmatch(source)
        assert match, "source for parse() must be validated by slice()"

        path_str = match.group('path').strip()
        path = parse_path(path_str)

        content = match.group('content')

        return FileToolCall(path, content)

__all__ = [
    'FileTool',
    'FileToolCall',
]
