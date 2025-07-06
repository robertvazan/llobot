from __future__ import annotations
from datetime import datetime
from functools import lru_cache
from llobot.chats import ChatRole
from llobot.knowledge import Knowledge
from llobot.scorers.knowledge import KnowledgeScorer
from llobot.crammers.knowledge import KnowledgeCrammer
from llobot.crammers.deletions import DeletionCrammer
from llobot.scrapers import Scraper
from llobot.contexts import Context
from llobot.experts import Expert
from llobot.experts.requests import ExpertRequest
import llobot.text
import llobot.scorers.knowledge
import llobot.crammers.knowledge
import llobot.crammers.deletions
import llobot.scrapers
import llobot.experts

@lru_cache
def standard(*,
    relevance_scorer: KnowledgeScorer = llobot.scorers.knowledge.irrelevant(),
    crammer: KnowledgeCrammer = llobot.crammers.knowledge.standard(),
) -> Expert:
    def stuff(request: ExpertRequest) -> Context:
        knowledge = request.project.root.knowledge(request.cutoff) if request.project else Knowledge()
        scores = relevance_scorer(knowledge)
        return crammer.cram(knowledge, request.budget, scores, request.context)
    return llobot.experts.create(stuff)

@lru_cache
def retrieval(*,
    scraper: Scraper = llobot.scrapers.retrieval(),
    crammer: KnowledgeCrammer = llobot.crammers.knowledge.retrieval(),
    # Scoring is only used to pick the most likely document the user probably meant.
    # It's a bit controversial whether files should be picked by relevance, but it most likely does not hurt.
    relevance_scorer: KnowledgeScorer = llobot.scorers.knowledge.irrelevant(),
) -> Expert:
    def stuff(request: ExpertRequest) -> Context:
        knowledge = request.project.root.knowledge(request.cutoff) if request.project else Knowledge()
        scores = relevance_scorer(knowledge)
        messages = (message.content for message in request.prompt if message.role == ChatRole.USER)
        prompt = llobot.text.concat(*messages)
        retrievals = llobot.links.resolve_best(scraper.scrape_prompt(prompt), knowledge, scores)
        # It is important we do not use priority scorer here, because that one can use zero score to exclude files.
        return crammer.cram(knowledge, request.budget, llobot.scores.knowledge.coerce(retrievals), request.context)
    return llobot.experts.create(stuff)

# This expert is actually intended to be used together with other experts,
# because it only does something if there is some outdated knowledge in the context already.
@lru_cache
def updates(*,
    deletion_crammer: DeletionCrammer = llobot.crammers.deletions.standard(),
    update_crammer: KnowledgeCrammer = llobot.crammers.knowledge.updates(),
) -> Expert:
    def stuff(request: ExpertRequest) -> Context:
        fresh_knowledge = request.project.root.knowledge(request.cutoff) if request.project else Knowledge()
        context_knowledge = request.context.knowledge
        deletions = context_knowledge.keys() - fresh_knowledge.keys()
        output = deletion_crammer.cram(deletions, request.budget)
        # Cram all documents in the context and rely an the crammer to filter out exact duplicates.
        # We would ideally want to score relevance, but that's currently not possible, because score parameter is used for filtering.
        output += update_crammer.cram(fresh_knowledge, request.budget - output.cost, llobot.scores.knowledge.coerce(context_knowledge.keys()), request.context + output)
        return output
    return llobot.experts.create(stuff)

__all__ = [
    'standard',
    'retrieval',
    'updates',
]

