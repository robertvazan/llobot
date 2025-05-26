from __future__ import annotations
from functools import lru_cache
from llobot.experts import Expert
import llobot.knowledge.subsets.rust
import llobot.scorers.knowledge
import llobot.experts.coders

@lru_cache
def standard(*, relevance_scorer: KnowledgeScorer | KnowledgeSubset = llobot.knowledge.subsets.rust.relevant(), **kwargs) -> Expert:
    return llobot.experts.coders.standard(relevance_scorer=relevance_scorer, **kwargs)

__all__ = [
    'standard',
]

