"""
Script item for reading files.
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
from llobot.tools.script import ScriptItem

class ScriptCat(ScriptItem):
    """
    Tool that parses `cat ~/path` commands.

    When reading a file, this tool automatically discovers and reads overview
    files (like README.md) in the target file's parent directories.
    """
    _format: DocumentFormat
    _overviews: KnowledgeSubset

    def __init__(self, *, format: DocumentFormat | None = None, overviews: KnowledgeSubset | None = None):
        """
        Initializes a new ScriptCat.

        Args:
            format: The document format to use for output. Defaults to standard format.
            overviews: The subset identifying overview files. Defaults to standard overviews.
        """
        self._format = format or standard_document_format()
        self._overviews = overviews or overviews_subset()

    def execute(self, env: Environment, line: str) -> bool:
        try:
            parts = shlex.split(line)
        except ValueError:
            return False

        if len(parts) != 2 or parts[0] != 'cat':
            return False

        path_str = parts[1]

        path = parse_path(path_str)

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

                    context_env.add(ChatMessage(ChatIntent.SYSTEM, f"Reading also related `~/{p}`..."))
                    context_env.add(ChatMessage(ChatIntent.SYSTEM, listing))

        # 2. Load target file
        content = project.read(path)
        if content is None:
            raise ValueError(f"File not found: ~/{path}")

        listing = self._format.render(path, content)

        if any(listing in msg.content for msg in context):
            context_env.add(ChatMessage(ChatIntent.STATUS, f"File `~/{path}` is already in the context."))
            return True

        context_env.add(ChatMessage(ChatIntent.SYSTEM, listing))
        return True

__all__ = [
    'ScriptCat',
]
