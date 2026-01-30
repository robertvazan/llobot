"""
Autonomy interface and implementations for agents.
"""
from __future__ import annotations
from llobot.utils.values import ValueTypeMixin

class Autonomy(ValueTypeMixin):
    """
    Defines the autonomy level of an agent.
    """
    @property
    def autorun(self) -> bool:
        """
        Indicates whether the agent should run tool calls automatically.
        """
        return False

class NoAutonomy(Autonomy):
    """
    Agent has no autonomy and requires user approval for all actions.
    """
    @property
    def autorun(self) -> bool:
        return False

class StepAutonomy(Autonomy):
    """
    Agent has limited autonomy to execute all tool calls within one response.
    """
    @property
    def autorun(self) -> bool:
        return True

__all__ = [
    'Autonomy',
    'NoAutonomy',
    'StepAutonomy',
]
