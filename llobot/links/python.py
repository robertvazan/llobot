from __future__ import annotations
from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.links import Link
import llobot.links

# Contains absolute slash-separated module path (without the leading slash).
#
# Example mappings from knowledge path to module link's path:
# - foo/bar.py -> foo/bar
# - foo/bar/__init__.py -> foo/bar
# - foo.py -> foo
# - __init__.py -> .
class _AbsolutePythonLink(Link):
    path: Path

    def __init__(self, path: Path):
        self.path = path

    def __eq__(self, other) -> bool:
        if not isinstance(other, _AbsolutePythonLink):
            return NotImplemented
        return self.path == other.path

    def __hash__(self) -> int:
        return hash(self.path)

    def __str__(self) -> str:
        return str(self.path)

    def matches(self, path: Path, content: str = '') -> bool:
        if path.name == '__init__.py':
            return path.parent == self.path
        else:
            return path.name == self.path.name + '.py' and path.parent == self.path.parent

    def resolve(self, knowledge: Knowledge) -> set[Path]:
        py_path = self.path.with_suffix('.py')
        if py_path in knowledge:
            return {py_path}
        init_path = self.path/'__init__.py'
        if init_path in knowledge:
            return {init_path}
        return set()

# Same as above but extra leading path segments in knowledge paths are ignored.
# The relative path encoded in the link can thus be resolved relative to directory in the knowledge.
# We however wouldn't allow '.' path as that would match every __init__.py in the project.
class _RelativePythonLink(Link):
    parts: tuple[str]

    def __init__(self, path: Path):
        self.parts = path.parts
        # Don't allow '.' paths.
        assert len(self.parts) > 0

    def __str__(self) -> str:
        return str(Path(*self.parts))

    def __eq__(self, other) -> bool:
        if not isinstance(other, _RelativePythonLink):
            return NotImplemented
        return self.parts == other.parts

    def __hash__(self) -> int:
        return hash(self.parts)

    def matches(self, path: Path, content: str = '') -> bool:
        if path.name == '__init__.py':
            parts = path.parts[:-1]
            return len(parts) >= len(self.parts) and parts[-len(self.parts):] == self.parts
        elif path.name == self.parts[-1] + '.py':
            parts = path.parts
            return len(parts) >= len(self.parts) and parts[-len(self.parts):-1] == self.parts[:-1]
        else:
            return False

    def _resolve(self, knowledge: Knowledge, indexes: dict[type, object] | None = None) -> set[Path]:
        py_path = Path(*self.parts[:-1], self.parts[-1] + '.py')
        init_path = Path(*self.parts, '__init__.py')
        for path in (py_path, init_path):
            abbreviated = llobot.links.abbreviated(path)
            resolved = abbreviated.resolve_indexed(knowledge, indexes) if indexes is not None else abbreviated.resolve(knowledge)
            if resolved:
                return resolved
        return set()

    def resolve(self, knowledge: Knowledge) -> set[Path]:
        return self._resolve(knowledge)

    def resolve_indexed(self, knowledge: Knowledge, indexes: dict[type, object]) -> set[Path]:
        return self._resolve(knowledge, indexes)

# Examples:
# foo/bar/__init__.py -> /foo/bar
# foo/bar.py -> /foo/bar
# __init__.py -> /
def _parse_path(path: Path) -> Path:
    path = '/'/path.with_suffix('')
    if path.name == '__init__':
        path = path.parent
    return path

# Example: foo.bar -> foo/bar
def _parse_relative(module: str) -> Path:
    return Path(module.replace('.', '/'))

# Example: foo.bar -> /foo/bar
def _parse_absolute(module: str) -> Path:
    return '/'/_parse_relative(module)

# Examples:
#
# foo -> /foo
# foo.bar -> /foo/bar
# . -> .
# .. -> ..
# ... -> ../..
# .foo -> foo
# .foo.bar -> foo/bar
# ..foo -> ../foo
#
# The resulting path is then resolved against source path
# except for absolute module references, which have unknown base path.
def _parse_from(module: str, source: Path | None) -> Path:
    if not module.startswith('.'):
        # We don't know base path of absolute imports.
        return _parse_relative(module)
    module = module[1:]
    root = _parse_path(source) if source else None
    while module.startswith('.'):
        root = root.parent if root and root != Path('/') else None
        module = module[1:]
    if not module:
        return root or Path('.')
    if not root:
        return _parse_relative(module)
    return root/_parse_relative(module)

def module(module: str) -> Link:
    return _RelativePythonLink(_parse_relative(module))

def from_path(path: Path | str) -> Link | None:
    path = Path(path)
    if path.suffix != '.py':
        return None
    return _AbsolutePythonLink(_parse_path(path))

def from_import(module: str) -> Link:
    return _RelativePythonLink(_parse_relative(module))

def from_from(module: str, *, path: Path | None = None) -> Link | None:
    parsed = _parse_from(module, path)
    if parsed.is_absolute():
        return _AbsolutePythonLink(parsed.relative_to('/'))
    elif parsed.parts:
        return _RelativePythonLink(parsed)
    else:
        return None

def from_import_item(module: str, item: str, *, path: Path | None = None) -> Link:
    base = _parse_from(module, path)
    if not base:
        return _RelativePythonLink(Path(item))
    elif base.is_absolute():
        return _AbsolutePythonLink(base.relative_to('/')/item)
    else:
        return _RelativePythonLink(base/item)

__all__ = [
    'module',
    'from_path',
    'from_import',
    'from_from',
    'from_import_item',
]

