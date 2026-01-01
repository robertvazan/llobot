"""
Tool for editing files using search and replace.
"""
from __future__ import annotations
from pathlib import PurePosixPath
import re
from typing import Iterable
from llobot.environments import Environment
from llobot.environments.projects import ProjectEnv
from llobot.environments.tools import ToolEnv
from llobot.formats.paths import parse_path
from llobot.tools import ToolCall
from llobot.tools.block import BlockTool
from llobot.utils.text import normalize_document

class EditToolCall(ToolCall):
    _path: PurePosixPath
    _search: str
    _replace: str

    def __init__(self, path: PurePosixPath, search: str, replace: str):
        self._path = path
        self._search = search
        self._replace = replace

    @property
    def title(self) -> str:
        return f"edit ~/{self._path}"

    def execute(self, env: Environment):
        project = env[ProjectEnv].union
        env[ToolEnv].log(f"Editing ~/{self._path}...")

        # Ensure consistent normalization for matching logic
        raw_content = project.read(self._path)
        if raw_content is None:
            raise FileNotFoundError(f"File not found: {self._path}")
        content = normalize_document(raw_content)

        search_block = normalize_document(self._search)
        replace_block = normalize_document(self._replace)

        if not search_block:
             raise ValueError("Search block cannot be empty.")

        matches = []
        start = 0
        while True:
            idx = content.find(search_block, start)
            if idx == -1:
                break

            # Check if match is at the start of a line
            if idx == 0 or content[idx - 1] == '\n':
                matches.append(idx)

            start = idx + 1

        if not matches:
            raise ValueError("Search block not found in file (must match whole lines).")
        if len(matches) > 1:
            raise ValueError(f"Search block found {len(matches)} times. Context is ambiguous.")

        match_index = matches[0]
        new_content = (
            content[:match_index] +
            replace_block +
            content[match_index + len(search_block):]
        )

        project.write(self._path, normalize_document(new_content))
        env[ToolEnv].log("File was edited.")

_EDIT_SLICE_RE = re.compile(
    r'^<details>\s*<summary>\s*Edit:\s*(?P<path>.+?)\s*</summary>\s*'
    r'^(?P<fence>`{3,})(?P<lang>[^`\n]*)\s*\n'
    r'(?P<content>.*?)'
    r'^(?P=fence)\s*</details>',
    re.DOTALL | re.MULTILINE
)

class EditTool(BlockTool):
    """
    Tool that parses edit listings in the format:
    <details>
    <summary>Edit: ~/path/to/file</summary>

    ```lang
    search content
    @@@
    replace content
    ```

    </details>
    """
    def slice(self, env: Environment, source: str, at: int) -> int:
        match = _EDIT_SLICE_RE.match(source, pos=at)
        if not match:
            return 0
        return match.end() - at

    def parse(self, env: Environment, source: str) -> Iterable[ToolCall]:
        match = _EDIT_SLICE_RE.fullmatch(source)
        assert match, "source for parse() must be validated by slice()"

        path_str = match.group('path').strip()
        path = parse_path(path_str)
        fence = match.group('fence')
        content = match.group('content')

        if re.search(r'^`{%d,}' % len(fence), content, re.MULTILINE):
            raise ValueError(f"Content contains a line starting with {len(fence)} or more backticks. Enclose the block in more backticks.")

        lines = content.splitlines(keepends=True)
        candidates = []
        for i, line in enumerate(lines):
            stripped = line.rstrip('\n\r')
            if len(stripped) >= 3 and all(c == '@' for c in stripped):
                candidates.append((i, len(stripped)))

        if not candidates:
            raise ValueError("Edit block must contain a separator line with 3 or more '@' characters.")

        max_len = max(l for _, l in candidates)
        best_candidates = [i for i, l in candidates if l == max_len]

        if len(best_candidates) > 1:
            raise ValueError(f"Ambiguous separator: multiple lines with {max_len} '@' characters found.")

        sep_idx = best_candidates[0]

        search = "".join(lines[:sep_idx])
        replace = "".join(lines[sep_idx+1:])

        yield EditToolCall(path, search, replace)

__all__ = [
    'EditTool',
    'EditToolCall',
]
