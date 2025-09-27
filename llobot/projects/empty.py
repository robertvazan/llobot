"""
A project that is empty.
"""
from __future__ import annotations
from llobot.projects import Project
from llobot.utils.values import ValueTypeMixin

class EmptyProject(Project, ValueTypeMixin):
    """
    A project that represents the absence of a project, containing no zones,
    prefixes, or items. It is a singleton-by-value.
    """
    pass

__all__ = [
    'EmptyProject',
]
