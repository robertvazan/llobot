"""
Tool execution environment.
"""
from __future__ import annotations
from typing import Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from llobot.tools import Tool

class ToolEnv:
    """
    Environment component for accumulating tool execution logs and managing tools.

    This environment manages two streams of text produced by tools:
    - Log: Internal execution details, errors, and status updates (via `log()`).
    - Output: User-visible content produced by the tool, such as file listings (via `output()`).
    """
    _log: list[str]
    _output: list[str]
    _tools: set[Tool]
    _cached_tools: list[Tool] | None

    def __init__(self):
        self._log = []
        self._output = []
        self._tools = set()
        self._cached_tools = None

    def log(self, message: str):
        """
        Appends a message to the tool execution log.

        Args:
            message: The message to log.
        """
        self._log.append(message)

    def flush_log(self) -> str:
        """
        Returns the accumulated log and clears the buffer.

        Returns:
            The joined log messages separated by newlines.
        """
        result = '\n'.join(self._log)
        self._log.clear()
        return result

    def output(self, content: str):
        """
        Appends content to the tool execution output.

        The output is intended to be displayed to the user, typically after the
        execution log.

        Args:
            content: The content to append.
        """
        self._output.append(content)

    def flush_output(self) -> str:
        """
        Returns the accumulated output and clears the buffer.

        Returns:
            The joined output strings separated by double newlines.
        """
        result = '\n\n'.join(self._output)
        self._output.clear()
        return result

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
