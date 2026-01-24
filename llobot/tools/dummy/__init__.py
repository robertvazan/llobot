"""
Defines the `DummyTool` interface and implementations.

Submodules
----------
code
    Dummy tool for skipping generic code blocks.
fenced
    Dummy tool for reporting unrecognized fenced blocks.
"""
from __future__ import annotations
from llobot.tools.block import BlockTool

class DummyTool(BlockTool):
    """
    Marker interface for tools that only skip content.
    """
    pass

__all__ = [
    'DummyTool',
]
