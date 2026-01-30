"""
Defines CrammerChain for sequencing multiple crammers.
"""
from __future__ import annotations
from typing import Sequence
from llobot.crammers import Crammer
from llobot.environments import Environment

class CrammerChain(Crammer):
    """
    A chain of crammers that are executed in sequence.

    This crammer allows combining multiple crammers into a single unit.
    The constructor flattens any nested chains passed to it.
    """
    crammers: Sequence[Crammer]

    def __init__(self, *crammers: Crammer):
        """
        Creates a new chain of crammers.

        Args:
            *crammers: Crammers to include in the chain. Nested chains are flattened.
        """
        flat_crammers: list[Crammer] = []
        for crammer in crammers:
            if isinstance(crammer, CrammerChain):
                flat_crammers.extend(crammer.crammers)
            else:
                flat_crammers.append(crammer)
        self.crammers = tuple(flat_crammers)

    def cram(self, env: Environment) -> None:
        for crammer in self.crammers:
            crammer.cram(env)

__all__ = [
    'CrammerChain',
]
