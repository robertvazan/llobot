from __future__ import annotations
from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.links import Link
import llobot.links

# Contains absolute slash-separated module path (without the leading slash).
#
# Example mappings from knowledge path to module link's path:
# - foo/bar.rs -> foo/bar
# - foo/bar/mod.rs -> foo/bar
# - foo.rs -> foo
# - mod.rs -> .
#
# Since Rust links could be pointing to the item inside the file, we have to consider all parents of the link as alternative links.
# So a link like x/y will match x/y/mod.rs, x/y.rs, x/mod.rs, x.rs, and mod.rs.
# We will try to match the longest path we can find in the knowledge to avoid unnecessary links to top-level modules.
class _AbsoluteRustLink(Link):
    # This may be empty if the path is '.'.
    parts: tuple[str]

    def __init__(self, path: Path):
        self.parts = path.parts

    def __str__(self) -> str:
        return str(Path(*self.parts))

    def __eq__(self, other) -> bool:
        if not isinstance(other, _AbsoluteRustLink):
            return NotImplemented
        return self.parts == other.parts

    def __hash__(self) -> int:
        return hash(self.parts)

    def matches(self, path: Path, content: str = '') -> bool:
        if path.name == 'mod.rs':
            parts = path.parts[:-1]
            return parts == self.parts[:len(parts)]
        elif self.parts and path.name == self.parts[-1] + '.rs':
            parts = path.parts
            return len(parts) <= len(self.parts) and parts[:-1] == self.parts[:len(parts)-1]
        else:
            return False

    def resolve(self, knowledge: Knowledge) -> set[Path]:
        # Return the longest matching path. This is different from matches() above, which returns everything.
        for length in reversed(range(1, len(self.parts) + 1)):
            rs_path = Path(*self.parts[:length-1], self.parts[length-1] + '.rs')
            if rs_path in knowledge:
                return {rs_path}
            mod_path = Path(*self.parts[:length], 'mod.rs')
            if mod_path in knowledge:
                return {mod_path}
        if Path('mod.rs') in knowledge:
            return {Path('mod.rs')}
        return set()

# Same as above but extra leading path segments in knowledge paths are ignored.
# The relative path encoded in the link can thus be resolved relative to directory in the knowledge.
# We however wouldn't allow '.' path as that would match every mod.rs in the project.
class _RelativeRustLink(Link):
    parts: tuple[str]

    def __init__(self, path: Path):
        self.parts = path.parts
        # Don't allow '.' paths.
        assert len(self.parts) > 0

    def __str__(self) -> str:
        return str(Path(*self.parts))

    def __eq__(self, other) -> bool:
        if not isinstance(other, _RelativeRustLink):
            return NotImplemented
        return self.parts == other.parts

    def __hash__(self) -> int:
        return hash(self.parts)

    def matches(self, path: Path, content: str = '') -> bool:
        if path.name == 'mod.rs':
            parts = path.parts[:-1]
            for length in range(1, min(len(self.parts), len(parts)) + 1):
                if self.parts[:length] == parts[-length:]:
                    return True
            return False
        else:
            parts = path.parts[:-1]
            for length in range(min(len(self.parts), len(parts))):
                if path.name == self.parts[length] + '.rs' and self.parts[:length] == parts[-length:]:
                    return True
            return False

    def _resolve(self, knowledge: Knowledge, indexes: dict[type, object] | None = None) -> set[Path]:
        # Return the longest matching path. This is different from matches() above, which returns everything.
        for length in reversed(range(1, len(self.parts) + 1)):
            rs_path = Path(*self.parts[:length-1], self.parts[length-1] + '.rs')
            mod_path = Path(*self.parts[:length], 'mod.rs')
            for path in (rs_path, mod_path):
                abbreviated = llobot.links.abbreviated(path)
                resolved = abbreviated.resolve_indexed(knowledge, indexes) if indexes is not None else abbreviated.resolve(knowledge)
                if resolved:
                    return resolved
        return set()

    def resolve(self, knowledge: Knowledge) -> set[Path]:
        return self._resolve(knowledge)

    def resolve_indexed(self, knowledge: Knowledge, indexes: dict[type, object]) -> set[Path]:
        return self._resolve(knowledge, indexes)

# Path is relative to knowledge root.
# Input path is already without .rs or /mod.rs suffix.
def absolute(path: Path) -> Link:
    return _AbsoluteRustLink(path)

# Path is relative to any directory in the knowledge.
def relative(path: Path) -> Link:
    return _RelativeRustLink(path)

def _source_path(source: Path) -> Path:
    if source.name == 'mod.rs':
        return source.parent
    else:
        return source.with_suffix('')

def submodule(source: Path, name: str) -> Link:
    return absolute(_source_path(source)/name)

# There are limits to simple parsing of Rust simple paths.
# It will not work if the path starts with a symbol that was previously imported by another use statement.
# This also wouldn't follow symbols forwarded via "pub use".
def use(source: Path, path: str) -> Link | None:
    if not path:
        return None
    # Paths starting with root namespace are uncommon and we cannot handle them well.
    if path.startswith('::'):
        return None
    # We will save ourselves a lot of overhead by filtering out std imports early.
    if path.startswith('std::') or path == 'std':
        return None
    resolved = _source_path(source)
    segments = path.split('::')
    if segments[0] in ('self', 'crate', '$crate'):
        if segments[0] == 'self':
            pass
        else:
            # Find the nearest parent named 'src' or 'tests'.
            for parent in source.parents:
                if parent.name in ('src', 'tests'):
                    resolved = parent.parent/'src'
                    break
            else:
                # If no src or tests parent was found, the code has non-standard structure and we cannot find the the crate root.
                return None
        segments = segments[1:]
    for segment in segments:
        # We will just ignore wildcards. Theoretically, we should scan for files under the concrete module,
        # but that's complicated and wildcards are rarely used to enumerate module files anyway.
        # We will assume most wildcards are enumerating items inside of a file and it is therefore safe to ignore them in paths.
        if segment == '*':
            break
        # Special path component in the middle of the path is probably an error. Ignore the path.
        if segment in ('self', 'crate', '$crate'):
            return None
        # If it doesn't look like module name, stop here. This saves some overhead.
        if not segment.isidentifier():
            break
        if segment == 'super':
            resolved = resolved.parent
        else:
            resolved = resolved/segment
    return absolute(resolved)

__all__ = [
    'absolute',
    'relative',
    'submodule',
    'use',
]

