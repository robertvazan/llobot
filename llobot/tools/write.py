"""
Tool for writing files from document listings.
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

class WriteTool(FencedTool):
    """
    Tool that parses document listings in the format:
    <details>
    <summary>Write: ~/path/to/hello.py</summary>

    ```python
    +def main():
    +    print("Hello, world!")
    +
    +if __name__ == "__main__":
    +    main()
    ```

    </details>

    Lines inside the block are expected to be prefixed with `+`. If any line
    lacks the prefix, the tool will still process the file but will add a warning
    to the context.
    """
    def match_fenced(self, env: Environment, name: str, header: str, content: str) -> bool:
        return name in {'Write', 'File'}

    def execute_fenced(self, env: Environment, name: str, header: str, content: str) -> bool:
        if name == 'File':
            env[ContextEnv].add(ChatMessage(ChatIntent.SYSTEM, "Warning: Use 'Write' tool to create or update files, not 'File'."))

        path_str = header

        path = parse_path(path_str)
        project = env[ProjectEnv].union
        knowledge_env = env[KnowledgeEnv]

        # Allow writing new files, but require existing files to be known first.
        if project.read(path) is not None and path not in knowledge_env:
            raise PermissionError(f"Safety: File `~/{path}` must be read before it can be overwritten.")

        lines = content.splitlines()

        if any(not line.startswith('+') for line in lines):
            env[ContextEnv].add(ChatMessage(ChatIntent.SYSTEM, "Warning: Prefix every line in the write tool call with a '+'."))

        new_content = '\n'.join(line[1:] if line.startswith('+') else line for line in lines)

        project.write(path, normalize_document(new_content))

        # Store exact content as requested.
        # This ensures that if normalization changed the content, the next read
        # will retrieve the normalized version from disk (which won't match this
        # unnormalized version) and correctly reload the file into context.
        knowledge_env.add(path, new_content)

        env[ContextEnv].add(ChatMessage(ChatIntent.SYSTEM, f"✅ Written `~/{path}`"))
        return True

__all__ = [
    'WriteTool',
]
