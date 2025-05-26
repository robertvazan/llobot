from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.links import Link

# Contains absolute slash-separated module path (without the leading slash).
#
# Example mappings from knowledge path to module link's path:
# - foo/bar.py -> foo/bar
# - foo/bar/__init__.py -> foo/bar
# - foo.py -> foo
# - __init__.py -> .
@dataclass(frozen=True)
class _PythonLink(Link):
    path: Path

    def matches(self, path: Path, content: str = '') -> bool:
        if path.name == '__init__.py':
            return path.parent == self.path
        else:
            return path.name == self.path.name + '.py' and path.parent == self.path.parent

    def resolve(self, knowledge: Knowledge) -> set[Path]:
        matches = set()
        py_path = self.path.with_suffix('.py')
        if py_path in knowledge:
            matches.add(py_path)
        init_path = self.path/'__init__.py'
        if init_path in knowledge:
            matches.add(init_path)
        return matches

# Strips the initial slash from the path before constructing the link.
def _to_link(path: Path) -> Link:
    return _PythonLink(path.relative_to(Path('/')))

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
# foo -> /foo
# foo.bar -> /foo/bar
# . -> .
# .. -> ..
# ... -> ../..
# .foo -> foo
# .foo.bar -> foo/bar
# ..foo -> ../foo
def _parse_from(module: str) -> Path:
    if not module.startswith('.'):
        return _parse_absolute(module)
    module = module[1:]
    root = Path('.')
    while module.startswith('.'):
        root = root/'..'
        module = module[1:]
    if not module:
        return root
    return root/_parse_relative(module)

def module(module: str) -> Link:
    return _to_link(_parse_absolute(module))

def from_path(path: Path | str) -> Link | None:
    path = Path(path)
    if path.suffix != '.py':
        return None
    return _to_link(_parse_path(path))

def from_import(module: str) -> Link:
    return _to_link(_parse_absolute(module))

def from_from(module: str, *, path: Path = Path('__init__.py')) -> Link:
    return _to_link(_parse_path(path)/_parse_from(module))

def from_import_item(module: str, item: str, *, path: Path = Path('__init__.py')) -> Link:
    return _to_link(_parse_path(path)/_parse_from(module)/item)

__all__ = [
    'module',
    'from_path',
    'from_import',
    'from_from',
    'from_import_item',
]

