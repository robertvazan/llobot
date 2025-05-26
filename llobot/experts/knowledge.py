from __future__ import annotations
from datetime import datetime
from functools import lru_cache
from llobot.knowledge import Knowledge
from llobot.scorers.ranks import RankScorer
from llobot.scorers.knowledge import KnowledgeScorer
from llobot.crammers.knowledge import KnowledgeCrammer
from llobot.scrapers import Scraper
from llobot.contexts import Context
from llobot.experts import Expert
from llobot.experts.requests import ExpertRequest
import llobot.scores.knowledge
import llobot.scorers.ranks
import llobot.scorers.knowledge
import llobot.crammers.knowledge
import llobot.scrapers
import llobot.experts

@lru_cache
def standard(*,
    scope_scorer: RankScorer = llobot.scorers.ranks.fast(),
    relevance_scorer: KnowledgeScorer = llobot.scorers.knowledge.irrelevant(),
    crammer: KnowledgeCrammer = llobot.crammers.knowledge.standard(),
) -> Expert:
    def stuff(request: ExpertRequest) -> Context:
        knowledge = request.scope.project.knowledge(request.cutoff) if request.scope else Knowledge()
        scores = llobot.scores.knowledge.scope(knowledge, request.scope, scope_scorer) * relevance_scorer(knowledge)
        return crammer.cram(knowledge, request.budget, scores, request.context)
    return llobot.experts.create(stuff)

@lru_cache
def retrieval(*,
    scraper: Scraper = llobot.scrapers.retrieval(),
    crammer: KnowledgeCrammer = llobot.crammers.knowledge.retrieval(),
    # Scoring is only used to pick the most likely document the user probably meant.
    scope_scorer: RankScorer = llobot.scorers.ranks.fast(),
    # It's a bit controversial whether files should be picked by relevance, but it most likely does not hurt.
    relevance_scorer: KnowledgeScorer = llobot.scorers.knowledge.irrelevant(),
) -> Expert:
    def stuff(request: ExpertRequest) -> Context:
        knowledge = request.scope.project.knowledge(request.cutoff) if request.scope else Knowledge()
        scores = llobot.scores.knowledge.scope(knowledge, request.scope, scope_scorer) * relevance_scorer(knowledge)
        retrievals = llobot.links.resolve_best(scraper.scrape_prompt(request.prompt), knowledge, scores)
        # It is important we do not use priority scorer here, because that one can use zero score to exclude files.
        return crammer.cram(knowledge, request.budget, llobot.scores.knowledge.coerce(retrievals), request.context)
    return llobot.experts.create(stuff)

__all__ = [
    'standard',
    'retrieval',
]

