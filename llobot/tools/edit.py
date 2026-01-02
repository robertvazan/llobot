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
    _index: int
    _total: int

    def __init__(self, path: PurePosixPath, search: str, replace: str, index: int = 1, total: int = 1):
        self._path = path
        self._search = search
        self._replace = replace
        self._index = index
        self._total = total

    @property
    def title(self) -> str:
        base = f"edit ~/{self._path}"
        if self._total > 1:
            return f"{base} (part {self._index} of {self._total})"
        return base

    def execute(self, env: Environment):
        project = env[ProjectEnv].union

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

_CODE_BLOCK_RE = re.compile(
    r'^(?P<fence>`{3,})(?P<lang>[^`\n]*)\s*\n'
    r'(?P<content>.*?)'
    r'^(?P=fence)(?=\s|$)',
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

    Multiple code blocks can be provided in the same tool call to perform
    multiple edits on the same file sequentially.
    """
    def slice(self, env: Environment, source: str, at: int) -> int:
        # Match the header
        # Using match with pos checks at that position. ^ matches start of string,
        # but since 'source' is passed as is, we rely on 'at' being start of line
        # and checking source[at:].
        header_match = re.match(r'^<details>\s*<summary>\s*Edit:\s*.+?\s*</summary>', source[at:])
        if not header_match:
            return 0

        cursor = at + header_match.end()
        length = len(source)

        in_code_block = False
        fence_len = 0

        while cursor < length:
            try:
                eol = source.index('\n', cursor)
            except ValueError:
                eol = length

            line = source[cursor:eol]

            # Strictly match fences at the start of the line to be consistent with parse()
            # and Markdown code block rules used in this project.
            fence_match = re.match(r'^(`{3,})', line)

            if in_code_block:
                # Check for code block end
                if fence_match:
                    if len(fence_match.group(1)) >= fence_len:
                        in_code_block = False
                        fence_len = 0
            else:
                # Check for closing tag
                if re.fullmatch(r'\s*</details>\s*', line):
                    # Found the closing tag outside of a code block
                    return (eol + 1) - at if eol < length else length - at

                # Check for code block start
                if fence_match:
                    in_code_block = True
                    fence_len = len(fence_match.group(1))

            cursor = eol + 1

        return 0

    def parse(self, env: Environment, source: str) -> Iterable[ToolCall]:
        # Header match is guaranteed by slice
        header_match = re.match(r'^<details>\s*<summary>\s*Edit:\s*(?P<path>.+?)\s*</summary>', source)
        if not header_match:
             raise ValueError("Invalid edit tool format header")

        path_str = header_match.group('path').strip()
        path = parse_path(path_str)

        # Extract body: from end of header to (start of) closing tag
        body_start = header_match.end()
        body = source[body_start:]

        # Find the last </details> that closes the block.
        # Since slice() ensures the block ends with </details> (possibly followed by newline),
        # we can safely strip it.
        closing_match = re.search(r'\s*</details>\s*$', body)
        if closing_match:
            body = body[:closing_match.start()]

        blocks = list(_CODE_BLOCK_RE.finditer(body))
        if not blocks:
            raise ValueError("Edit tool call must contain at least one code block.")

        total = len(blocks)
        for i, block_match in enumerate(blocks, 1):
            content = block_match.group('content')
            lines = content.splitlines(keepends=True)
            candidates = []
            for j, line in enumerate(lines):
                stripped = line.rstrip('\n\r')
                if len(stripped) >= 3 and all(c == '@' for c in stripped):
                    candidates.append((j, len(stripped)))

            if not candidates:
                raise ValueError("Edit block must contain a separator line with 3 or more '@' characters.")

            max_len = max(l for _, l in candidates)
            best_candidates = [j for j, l in candidates if l == max_len]

            if len(best_candidates) > 1:
                raise ValueError(f"Ambiguous separator: multiple lines with {max_len} '@' characters found.")

            sep_idx = best_candidates[0]

            search = "".join(lines[:sep_idx])
            replace = "".join(lines[sep_idx+1:])

            yield EditToolCall(path, search, replace, index=i, total=total)

__all__ = [
    'EditTool',
    'EditToolCall',
]
