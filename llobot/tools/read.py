"""
Tool for reading files.
"""
from __future__ import annotations
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.projects import ProjectEnv
from llobot.environments.knowledge import KnowledgeEnv
from llobot.formats.documents import DocumentFormat, standard_document_format
from llobot.formats.paths import parse_path
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.knowledge.subsets.standard import overviews_subset
from llobot.projects.items import ProjectFile
from llobot.tools.fenced import FencedTool

class ReadTool(FencedTool):
    """
    Tool that parses read requests in the format:
    <details>
    <summary>Read: informal description</summary>

    ```
    ~/path/to/file1
    ~/path/to/file2
    ```

    </details>
    """
    _format: DocumentFormat
    _overviews: KnowledgeSubset

    def __init__(self, *, format: DocumentFormat | None = None, overviews: KnowledgeSubset | None = None):
        self._format = format or standard_document_format()
        self._overviews = overviews or overviews_subset()

    def match_fenced(self, env: Environment, name: str, header: str, content: str) -> bool:
        return name == 'Read'

    def execute_fenced(self, env: Environment, name: str, header: str, content: str) -> bool:
        project = env[ProjectEnv].union
        context_env = env[ContextEnv]
        knowledge_env = env[KnowledgeEnv]

        lines = content.splitlines()

        for line in lines:
            line = line.strip()
            if not line:
                continue

            path = parse_path(line)

            # 1. Load overviews
            parents = list(path.parents)
            parents.reverse()

            for parent in parents:
                items = sorted(project.items(parent), key=lambda i: i.path)
                for item in items:
                    if isinstance(item, ProjectFile) and item.path in self._overviews:
                        p = item.path
                        if p == path:
                            continue

                        content_str = project.read(p)
                        if content_str is None:
                            continue

                        if knowledge_env.get(p) == content_str:
                            continue

                        listing = self._format.render(p, content_str)

                        context_env.add(ChatMessage(ChatIntent.SYSTEM, f"Reading also related `~/{p}`..."))
                        context_env.add(ChatMessage(ChatIntent.SYSTEM, listing))
                        knowledge_env.add(p, content_str)

            # 2. Load target file
            content_str = project.read(path)
            if content_str is None:
                raise ValueError(f"File not found: ~/{path}")

            if knowledge_env.get(path) == content_str:
                context_env.add(ChatMessage(ChatIntent.STATUS, f"File `~/{path}` is already in the context."))
                continue

            listing = self._format.render(path, content_str)

            context_env.add(ChatMessage(ChatIntent.SYSTEM, listing))
            knowledge_env.add(path, content_str)

        return True

__all__ = [
    'ReadTool',
]
