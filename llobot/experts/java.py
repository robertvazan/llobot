from __future__ import annotations
from functools import cache, lru_cache
from importlib import resources
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.contexts import Context
from llobot.contexts.examples import ExampleChunk
from llobot.experts import Expert
from llobot.experts.requests import ExpertRequest
import llobot.text
import llobot.knowledge.subsets.java
import llobot.scorers.knowledge
import llobot.contexts
import llobot.experts
import llobot.experts.coders

@lru_cache
def standard(*, relevance_scorer: KnowledgeScorer | KnowledgeSubset = llobot.knowledge.subsets.java.relevant(), **kwargs) -> Expert:
    return llobot.experts.coders.standard(relevance_scorer=relevance_scorer, **kwargs)

@cache
def junit_relevant() -> KnowledgeSubset:
    return llobot.knowledge.subsets.java.regular() - llobot.knowledge.subsets.java.benchmarks()

@lru_cache
def junit(*,
    relevance_scorer: KnowledgeScorer | KnowledgeSubset = junit_relevant(),
    **kwargs
) -> Expert:
    editor = llobot.experts.coders.standard(relevance_scorer=relevance_scorer, **kwargs)
    def stuff(request: ExpertRequest) -> Context:
        chunks = editor(request).chunks
        tail_index = max((index + 1 for index, chunk in enumerate(chunks) if isinstance(chunk, ExampleChunk)), default=0)
        has_tests = lambda chunk: chunk.knowledge & llobot.knowledge.subsets.java.tests()
        withheld = [chunk for chunk in chunks[:tail_index] if has_tests(chunk)]
        filtered = [chunk for chunk in chunks[:tail_index] if not has_tests(chunk)]
        return llobot.contexts.compose(*filtered, *withheld, *chunks[tail_index:])
    return llobot.experts.create(stuff)

__all__ = [
    'standard',
    'junit_relevant',
    'junit',
]

