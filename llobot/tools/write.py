"""
Tool for writing files from document listings.
"""
from __future__ import annotations
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.projects import ProjectEnv
from llobot.formats.paths import parse_path
from llobot.tools.fenced import FencedTool
from llobot.utils.text import normalize_document

class WriteTool(FencedTool):
    """
    Tool that parses document listings in the format:
    <details>
    <summary>Write: ~/path/to/file</summary>

    ```lang
    content
    ```

    </details>
    """
    def match_fenced(self, env: Environment, name: str, header: str, content: str) -> bool:
        return name in {'Write', 'File'}

    def execute_fenced(self, env: Environment, name: str, header: str, content: str) -> bool:
        path_str = header

        path = parse_path(path_str)
        project = env[ProjectEnv].union

        project.write(path, normalize_document(content))

        if name == 'File':
            env[ContextEnv].add(ChatMessage(ChatIntent.SYSTEM, "Warning: Use 'Write' tool to create or update files, not 'File'."))

        env[ContextEnv].add(ChatMessage(ChatIntent.STATUS, f"Written `~/{path}`"))
        return True

__all__ = [
    'WriteTool',
]
