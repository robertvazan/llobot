from __future__ import annotations
from functools import lru_cache
from llobot.experts import Expert
import llobot.knowledge.subsets.python
import llobot.scorers.knowledge
import llobot.experts.coders

@lru_cache
def standard(*, relevance_scorer: KnowledgeScorer | KnowledgeSubset = llobot.knowledge.subsets.python.suffix(), **kwargs) -> Expert:
    return llobot.experts.coders.standard(relevance_scorer=relevance_scorer, **kwargs)

__all__ = [
    'standard',
]

