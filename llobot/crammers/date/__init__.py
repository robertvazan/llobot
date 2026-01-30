"""
Crammers for adding date and time information to the context.
"""
from __future__ import annotations
from functools import cache
from llobot.crammers import Crammer
from llobot.environments import Environment

class DateCrammer(Crammer):
    """
    Base class for crammers that add date information.
    """
    def cram(self, env: Environment) -> None:
        """
        Adds date information to the context.

        Args:
            env: The environment containing the context builder.
        """
        raise NotImplementedError

@cache
def standard_date_crammer() -> DateCrammer:
    """
    Returns the standard date crammer.
    """
    from llobot.crammers.date.simple import SimpleDateCrammer
    return SimpleDateCrammer()

__all__ = [
    'DateCrammer',
    'standard_date_crammer',
]
