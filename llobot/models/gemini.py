from __future__ import annotations
from llobot.models import Model
import llobot.models.openai

# Always specify context size. This must be a conscious cost-benefit decision.
def proprietary(name: str, context_size: int, auth: str, **kwargs) -> Model:
    return llobot.models.openai.compatible('https://generativelanguage.googleapis.com/v1beta/openai', 'gemini', name, context_size, auth=auth, **kwargs)

__all__ = [
    'proprietary',
]

