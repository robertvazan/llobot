"""
Tool execution environment.
"""
from __future__ import annotations
from typing import Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from llobot.tools import Tool

class ToolEnv:
    """
    Environment component for managing registered tools.
    """
    _tools: set[Tool]
    _cached_tools: list[Tool] | None

    def __init__(self):
        self._tools = set()
        self._cached_tools = None

    def register(self, tool: Tool):
        """
        Registers a tool if it is not already present.

        Args:
            tool: The tool to register.
        """
        if tool not in self._tools:
            self._tools.add(tool)
            self._cached_tools = None

    def register_all(self, tools: Iterable[Tool]):
        """
        Registers multiple tools.

        Args:
            tools: The tools to register.
        """
        changed = False
        for tool in tools:
            if tool not in self._tools:
                self._tools.add(tool)
                changed = True
        if changed:
            self._cached_tools = None

    @property
    def tools(self) -> list[Tool]:
        """
        Returns the list of registered tools.

        The tools are sorted by their string representation. Dummy tools are
        placed at the end of the list. Result is cached until more tools
        are registered.
        """
        if self._cached_tools is None:
            from llobot.tools.dummy import DummyTool

            # Sort by string representation for reproducibility
            sorted_tools = sorted(self._tools, key=str)

            # Separate dummy tools to the end
            normal_tools = [t for t in sorted_tools if not isinstance(t, DummyTool)]
            dummy_tools = [t for t in sorted_tools if isinstance(t, DummyTool)]

            self._cached_tools = normal_tools + dummy_tools

        return self._cached_tools

__all__ = [
    'ToolEnv',
]
