from __future__ import annotations
from functools import lru_cache
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.scrapers import Scraper
from llobot.scorers.ranks import RankScorer
from llobot.scorers.knowledge import KnowledgeScorer
from llobot.crammers.knowledge import KnowledgeCrammer
from llobot.crammers.examples import ExampleCrammer
from llobot.contexts import Context
from llobot.experts import Expert
from llobot.experts.requests import ExpertRequest
import llobot.scrapers
import llobot.scorers.ranks
import llobot.scorers.knowledge
import llobot.crammers.knowledge
import llobot.crammers.examples
import llobot.contexts
import llobot.experts
import llobot.experts.instructions
import llobot.experts.knowledge
import llobot.experts.examples

@lru_cache
def standard(*,
    instructions: Expert | str = '',
    retrieval_scraper: Scraper = llobot.scrapers.retrieval(),
    scope_scorer: RankScorer = llobot.scorers.ranks.fast(),
    relevance_scorer: KnowledgeScorer | KnowledgeSubset = llobot.scorers.knowledge.irrelevant(),
    knowledge_crammer: KnowledgeCrammer = llobot.crammers.knowledge.standard(),
    example_crammer: ExampleCrammer = llobot.crammers.examples.standard(),
    retrieval_crammer: KnowledgeCrammer = llobot.crammers.knowledge.retrieval(),
    knowledge_share: float = 1.0,
    example_share: float = 0.25,
    retrieval_share: float = 1.0,
) -> Expert:
    if isinstance(relevance_scorer, KnowledgeSubset):
        relevance_scorer = llobot.scorers.knowledge.relevant(relevance_scorer)
    instructions = llobot.experts.instructions.coerce(instructions)
    knowledge_expert = llobot.experts.knowledge.standard(scope_scorer=scope_scorer, relevance_scorer=relevance_scorer, crammer=knowledge_crammer)
    example_expert = llobot.experts.examples.standard(crammer=example_crammer)
    retrieval_expert = llobot.experts.knowledge.retrieval(scraper=retrieval_scraper, crammer=retrieval_crammer, scope_scorer=scope_scorer, relevance_scorer=relevance_scorer)
    def stuff(request: ExpertRequest) -> Context:
        # Budget distribution priorities: instructions, retrievals, examples, knowledge.
        system = instructions(request)
        remaining_budget = request.budget - system.cost
        retrieval_budget = min(remaining_budget, int(retrieval_share * request.budget))
        retrievals = retrieval_expert(request.replace(budget=retrieval_budget, context=request.context+system))
        remaining_budget -= retrievals.cost
        example_budget = min(remaining_budget, int(example_share * request.budget))
        examples = example_expert(request.replace(budget=example_budget, context=request.context+system+retrievals))
        remaining_budget -= examples.cost
        knowledge_budget = min(remaining_budget, int(knowledge_share * request.budget))
        knowledge = knowledge_expert(request.replace(budget=knowledge_budget, context=request.context+system+examples+retrievals))
        return system + knowledge + examples + retrievals
    return llobot.experts.create(stuff)

__all__ = [
    'standard',
]

