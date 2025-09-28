"""An empty project library."""
from __future__ import annotations
from llobot.projects.library import ProjectLibrary
from llobot.utils.values import ValueTypeMixin

class EmptyProjectLibrary(ProjectLibrary, ValueTypeMixin):
    """An empty project library that never finds any projects."""
    pass

__all__ = ['EmptyProjectLibrary']
