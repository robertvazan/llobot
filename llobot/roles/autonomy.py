"""
Autonomy interface and implementations for agents.
"""
from __future__ import annotations
from datetime import datetime, timedelta
from typing import TYPE_CHECKING
from llobot.utils.values import ValueTypeMixin
from llobot.utils.time import current_time
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.environments.context import ContextEnv

if TYPE_CHECKING:
    from llobot.environments import Environment

def _measure(env: Environment) -> tuple[int, datetime, int]:
    """
    Measures current resources usage in the environment.

    Returns:
        A tuple of (context_cost, current_time, turn_count).
    """
    builder = env[ContextEnv].builder
    # Measure context cost including message overhead
    context = builder.cost
    now = current_time()
    turns = sum(1 for m in builder.messages if m.intent == ChatIntent.RESPONSE)
    return context, now, turns

def _format_delta(delta: timedelta) -> str:
    """
    Formats a time delta into a human-readable string.
    """
    total_seconds = int(delta.total_seconds())
    minutes = total_seconds // 60
    seconds = total_seconds % 60

    parts = []
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if seconds > 0 or not parts:
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")

    return " ".join(parts)

class AutonomyPermit:
    """
    A permit that authorizes the agent to continue running automatically.
    """
    def valid(self, env: Environment) -> bool:
        """
        Checks if the permit is still valid.

        If the permit becomes invalid, this method may produce side effects,
        such as adding a status message to the environment explaining why.

        Args:
            env: The current environment.

        Returns:
            True if the agent is authorized to continue, False otherwise.
        """
        raise NotImplementedError

class NoAutonomyPermit(AutonomyPermit):
    """
    A permit that is never valid.
    """
    def valid(self, env: Environment) -> bool:
        return False

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

    def start(self, env: Environment) -> AutonomyPermit:
        """
        Starts an autonomous session/loop.

        Args:
            env: The environment.

        Returns:
            An AutonomyPermit that tracks resource usage.
        """
        return NoAutonomyPermit()

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

class LimitedAutonomyPermit(AutonomyPermit):
    """
    A permit that enforces resource limits.
    """
    _limits: LimitedAutonomy
    _start_context: int
    _start_time: datetime
    _start_turns: int
    _notified: bool

    def __init__(self, limits: LimitedAutonomy, start_context: int, start_time: datetime, start_turns: int):
        self._limits = limits
        self._start_context = start_context
        self._start_time = start_time
        self._start_turns = start_turns
        self._notified = False

    def valid(self, env: Environment) -> bool:
        if self._notified:
            return False

        # Measure current state
        current_context, now, current_turns = _measure(env)

        # Calculate deltas
        delta_context = current_context - self._start_context
        delta_time = now - self._start_time
        delta_turns = current_turns - self._start_turns

        # Check limits
        reason = None
        if delta_turns >= self._limits.turn_limit:
            reason = f"{self._limits.turn_limit} turns"
        elif delta_time >= self._limits.time_limit:
            reason = _format_delta(self._limits.time_limit)
        elif delta_context >= self._limits.context_limit:
            reason = f"{self._limits.context_limit} chars"

        if reason:
            env[ContextEnv].add(ChatMessage(ChatIntent.STATUS, f"Stopping to consult the user after {reason}."))
            self._notified = True
            return False

        return True

class LimitedAutonomy(Autonomy):
    """
    Agent has autonomy with resource limits.
    """
    _context_limit: int
    _time_limit: timedelta
    _turn_limit: int

    def __init__(self, context: int = 1_000_000, time: timedelta = timedelta(minutes=10), turns: int = 20):
        self._context_limit = context
        self._time_limit = time
        self._turn_limit = turns

    @property
    def autorun(self) -> bool:
        return True

    @property
    def context_limit(self) -> int:
        return self._context_limit

    @property
    def time_limit(self) -> timedelta:
        return self._time_limit

    @property
    def turn_limit(self) -> int:
        return self._turn_limit

    def start(self, env: Environment) -> AutonomyPermit:
        start_context, start_time, start_turns = _measure(env)
        return LimitedAutonomyPermit(self, start_context, start_time, start_turns)

__all__ = [
    'AutonomyPermit',
    'Autonomy',
    'NoAutonomyPermit',
    'NoAutonomy',
    'StepAutonomy',
    'LimitedAutonomyPermit',
    'LimitedAutonomy',
]
