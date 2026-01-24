"""
Script item for replacing text in files using regex patterns.

This is a simplified version of the `sd` tool that accepts syntax:
`sd pattern replacement ~/path`. The regex pattern is always case-sensitive.
Replacement templates use Rust syntax, which is translated to Python syntax.
"""
from __future__ import annotations
import re
import shlex
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.projects import ProjectEnv
from llobot.formats.paths import parse_path
from llobot.tools.script import ScriptItem
from llobot.utils.text import normalize_document


# Pattern to match Rust-style replacement references
_RUST_REPLACEMENT_RE = re.compile(
    r'\$\$'              # $$ - literal dollar
    r'|\$\{([^}]*)\}'    # ${name} - braced group name (capture group 1)
    r'|\$([0-9]+)'       # $N - numbered group (capture group 2)
    r'|\$([A-Za-z_]\w*)' # $name - named group (capture group 3)
)


def rust_to_python_replacement(template: str) -> str:
    """
    Translates a Rust-style replacement template to Python regex syntax.

    Rust replacement syntax:
    - `$1`, `$2`, ... for numbered capture groups
    - `$0` for the entire match
    - `$name` or `${name}` for named capture groups
    - `$$` for a literal `$`

    Python replacement syntax:
    - `\\1`, `\\2`, ... for numbered capture groups
    - `\\g<0>` for the entire match
    - `\\g<name>` for named capture groups
    - `$` is literal (no escaping needed)

    Args:
        template: The Rust-style replacement template.

    Returns:
        The Python-style replacement string.

    Raises:
        ValueError: If the template contains invalid group references.
    """
    def replace_match(match: re.Match) -> str:
        full = match.group(0)
        if full == '$$':
            return '$'
        braced_name = match.group(1)
        if braced_name is not None:
            if not braced_name:
                raise ValueError("Empty group name in replacement template: ${}")
            if not (braced_name[0].isalpha() or braced_name[0] == '_'):
                raise ValueError(f"Invalid group name in replacement template: ${{{braced_name}}}")
            if not all(c.isalnum() or c == '_' for c in braced_name):
                raise ValueError(f"Invalid group name in replacement template: ${{{braced_name}}}")
            return f'\\g<{braced_name}>'
        num = match.group(2)
        if num is not None:
            return '\\g<0>' if num == '0' else f'\\{num}'
        name = match.group(3)
        if name is not None:
            return f'\\g<{name}>'
        return full

    return _RUST_REPLACEMENT_RE.sub(replace_match, template)


class ScriptReplace(ScriptItem):
    """
    Tool that parses `sd pattern replacement ~/path` commands.

    This is a simplified version of the `sd` tool. The regex pattern is always
    interpreted as case-sensitive. The replacement template uses Rust syntax,
    which is translated to Python syntax before applying.
    """

    def execute(self, env: Environment, line: str) -> bool:
        try:
            parts = shlex.split(line)
        except ValueError:
            return False

        if len(parts) != 4 or parts[0] != 'sd':
            return False

        pattern = parts[1]
        replacement = parts[2]
        path_str = parts[3]

        path = parse_path(path_str)
        project = env[ProjectEnv].union

        content = project.read(path)
        if content is None:
            raise ValueError(f"File not found: ~/{path}")

        # Compile pattern as case-sensitive (default in Python)
        try:
            regex = re.compile(pattern)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")

        # Translate Rust replacement syntax to Python
        python_replacement = rust_to_python_replacement(replacement)

        # Perform replacement
        new_content, count = regex.subn(python_replacement, content)

        if count == 0:
            raise ValueError(f"Pattern not found in `~/{path}`: {pattern}")

        project.write(path, normalize_document(new_content))
        env[ContextEnv].add(ChatMessage(ChatIntent.STATUS, f"✅ Replaced {count} matches in `~/{path}`"))

        return True


__all__ = [
    'ScriptReplace',
    'rust_to_python_replacement',
]
