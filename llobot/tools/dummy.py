"""
Defines the `DummyTool` interface.
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
