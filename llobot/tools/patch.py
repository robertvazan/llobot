"""
Tool for patching files using unified diffs.
"""
from __future__ import annotations
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.projects import ProjectEnv
from llobot.environments.knowledge import KnowledgeEnv
from llobot.formats.paths import parse_path
from llobot.tools.fenced import FencedTool
from llobot.utils.text import normalize_document

class PatchTool(FencedTool):
    """
    Tool that parses patch listings in the format:
    <details>
    <summary>Patch: ~/path/to/file</summary>

    ```diff
    @@ ...
    - search content
    + replace content
    ```

    </details>
    """

    def match_fenced(self, env: Environment, name: str, header: str, content: str) -> bool:
        return name == 'Patch'

    def execute_fenced(self, env: Environment, name: str, header: str, content: str) -> bool:
        path_str = header
        diff = content

        path = parse_path(path_str)
        project = env[ProjectEnv].union
        knowledge_env = env[KnowledgeEnv]

        if path not in knowledge_env:
            raise PermissionError(f"Safety: File `~/{path}` must be read before it can be patched.")

        original_content = project.read(path)
        if original_content is None:
            raise FileNotFoundError(f"File not found: ~/{path}")

        file_content = normalize_document(original_content)

        try:
            hunks = self._parse_diff(diff)
        except ValueError as e:
            raise ValueError(f"Invalid patch for `~/{path}`: {e}") from e

        if not hunks:
            raise ValueError(f"No hunks found in patch for `~/{path}`.")

        current_content = file_content

        for i, (search_block, replace_block) in enumerate(hunks):
            hunk_num = i + 1
            if not search_block:
                raise ValueError(f"Patching `~/{path}` failed: Hunk {hunk_num} search block is empty.")

            matches = []
            start = 0
            while True:
                idx = current_content.find(search_block, start)
                if idx == -1:
                    break

                # Check start of line.
                # The search block is guaranteed to end with \n by _parse_diff, so we implicitly check end of line too.
                if idx == 0 or current_content[idx - 1] == '\n':
                    matches.append(idx)

                start = idx + 1

            if not matches:
                raise ValueError(f"Patching `~/{path}` failed: Hunk {hunk_num} search block not found.")

            if len(matches) > 1:
                raise ValueError(f"Patching `~/{path}` failed: Hunk {hunk_num} search block found {len(matches)} times. Context is ambiguous.")

            idx = matches[0]
            current_content = (
                current_content[:idx] +
                replace_block +
                current_content[idx + len(search_block):]
            )

        new_content = normalize_document(current_content)
        project.write(path, new_content)

        context_env = env[ContextEnv]
        context_env.add(ChatMessage(ChatIntent.STATUS, f"✅ Applied {len(hunks)} hunks to `~/{path}`."))

        return True

    def _parse_diff(self, diff: str) -> list[tuple[str, str]]:
        lines = diff.splitlines(keepends=True)
        # Ensure the last line ends with newline
        if lines and not lines[-1].endswith('\n'):
            lines[-1] += '\n'

        hunks = []
        search_lines = []
        replace_lines = []
        in_hunk = False

        for line in lines:
            if line.startswith('@@'):
                if in_hunk:
                    hunks.append(("".join(search_lines), "".join(replace_lines)))
                in_hunk = True
                search_lines = []
                replace_lines = []
                continue

            # Skip header lines before first hunk
            if not in_hunk:
                continue

            if line.startswith(' '):
                # Context
                content = line[1:].rstrip() + '\n'
                search_lines.append(content)
                replace_lines.append(content)
            elif line == '\n':
                # Empty line treated as empty context line
                content = '\n'
                search_lines.append(content)
                replace_lines.append(content)
            elif line.startswith('-'):
                # Delete
                search_lines.append(line[1:].rstrip() + '\n')
            elif line.startswith('+'):
                # Add
                replace_lines.append(line[1:].rstrip() + '\n')
            else:
                raise ValueError(f"Invalid diff line: {line.strip()!r}")

        if in_hunk:
            hunks.append(("".join(search_lines), "".join(replace_lines)))

        return hunks

__all__ = [
    'PatchTool',
]
