"""
Tool reader for tracking parsing position and statistics.
"""
from __future__ import annotations

class ToolReader:
    """
    Encapsulates the source string and current position for tool parsing.

    Tracks the number of parsed and successfully executed tool calls.
    """
    _source: str
    _position: int
    _tool_count: int
    _success_count: int

    def __init__(self, source: str):
        self._source = source
        self._position = 0
        self._tool_count = 0
        self._success_count = 0

    @property
    def source(self) -> str:
        """The full source string being parsed."""
        return self._source

    @property
    def position(self) -> int:
        """The current cursor position in the source string."""
        return self._position

    @property
    def tool_count(self) -> int:
        """The number of tool calls identified so far (excluding skips)."""
        return self._tool_count

    @property
    def success_count(self) -> int:
        """The number of tool calls that executed successfully."""
        return self._success_count

    def advance(self, length: int):
        """
        Moves the cursor forward by `length` and increments the tool call counter.

        This should be called when a tool call is identified.
        """
        self._check_bounds(length)
        self._position += length
        self._tool_count += 1

    def skip(self, length: int):
        """
        Moves the cursor forward by `length` without incrementing the tool call counter.

        This should be called for content that should be ignored (e.g., by dummy tools).
        """
        self._check_bounds(length)
        self._position += length

    def passed(self):
        """
        Increments the successful tool call counter.

        This should be called after a tool call has finished executing successfully.
        """
        self._success_count += 1

    def _check_bounds(self, length: int):
        if length < 0:
            raise ValueError(f"Advance/skip length must be non-negative: {length}")
        if self._position + length > len(self._source):
            raise IndexError(f"Advance/skip length {length} exceeds source bounds (pos {self._position}, len {len(self._source)})")

__all__ = [
    'ToolReader',
]
