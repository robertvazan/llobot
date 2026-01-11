"""
Tool for reading files.
"""
from __future__ import annotations
import shlex
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.projects import ProjectEnv
from llobot.formats.documents import DocumentFormat, standard_document_format
from llobot.formats.paths import parse_path
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.knowledge.subsets.standard import overviews_subset
from llobot.projects.items import ProjectFile
from llobot.tools import ToolCall
from llobot.tools.line import LineTool

class CatToolCall(ToolCall):
    """
    A tool call for reading a file.

    Executes a read operation for the specified file. As a side effect, it also
    identifies and reads overview files (e.g. README.md, __init__.py) in the
    target file's parent directories to provide context.
    """
    _path: str
    _format: DocumentFormat
    _overviews: KnowledgeSubset

    def __init__(self, path: str, format: DocumentFormat, overviews: KnowledgeSubset):
        self._path = path
        self._format = format
        self._overviews = overviews

    @property
    def title(self) -> str:
        return f"cat {self._path}"

    def execute(self, env: Environment):
        path = parse_path(self._path)

        project = env[ProjectEnv].union
        context_env = env[ContextEnv]
        context = context_env.build()

        # 1. Load overviews in parent directories, starting from root
        parents = list(path.parents)
        parents.reverse()

        for parent in parents:
            # Sort items to ensure deterministic order
            items = sorted(project.items(parent), key=lambda i: i.path)
            for item in items:
                if isinstance(item, ProjectFile) and item.path in self._overviews:
                    p = item.path
                    if p == path:
                        continue

                    content = project.read(p)
                    if content is None:
                        continue

                    listing = self._format.render(p, content)

                    if any(listing in msg.content for msg in context):
                        continue

                    context_env.add(ChatMessage(ChatIntent.SYSTEM, listing))
                    context_env.add(ChatMessage(ChatIntent.STATUS, f"Read also: ~/{p}"))

        # 2. Load target file
        content = project.read(path)
        if content is None:
            raise ValueError(f"File not found: ~/{path}")

        listing = self._format.render(path, content)

        if any(listing in msg.content for msg in context):
            context_env.add(ChatMessage(ChatIntent.STATUS, f"File ~/{path} is already in the context."))
            return

        context_env.add(ChatMessage(ChatIntent.SYSTEM, listing))

class CatTool(LineTool):
    """
    Tool that parses `cat ~/path` commands.

    When reading a file, this tool automatically discovers and reads overview
    files (like README.md) in the target file's parent directories.
    """
    _format: DocumentFormat
    _overviews: KnowledgeSubset

    def __init__(self, *, format: DocumentFormat | None = None, overviews: KnowledgeSubset | None = None):
        """
        Initializes a new CatTool.

        Args:
            format: The document format to use for output. Defaults to standard format.
            overviews: The subset identifying overview files. Defaults to standard overviews.
        """
        self._format = format or standard_document_format()
        self._overviews = overviews or overviews_subset()

    def matches_line(self, env: Environment, line: str) -> bool:
        try:
            parts = shlex.split(line)
        except ValueError:
            return False
        return len(parts) == 2 and parts[0] == 'cat'

    def parse_line(self, env: Environment, line: str) -> ToolCall:
        parts = shlex.split(line)
        # matches_line checks structure, but let's be safe
        if len(parts) != 2 or parts[0] != 'cat':
            raise ValueError(f"Invalid cat command: {line}")

        path = parts[1]

        return CatToolCall(path, self._format, self._overviews)

__all__ = [
    'CatTool',
    'CatToolCall',
]
