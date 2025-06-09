from __future__ import annotations
from functools import lru_cache
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.scrapers import Scraper
from llobot.scorers.ranks import RankScorer
from llobot.scorers.knowledge import KnowledgeScorer
from llobot.crammers.knowledge import KnowledgeCrammer
from llobot.crammers.deletions import DeletionCrammer
from llobot.crammers.examples import ExampleCrammer
from llobot.contexts import Context
from llobot.experts import Expert
from llobot.experts.requests import ExpertRequest
import llobot.scrapers
import llobot.scorers.ranks
import llobot.scorers.knowledge
import llobot.crammers.knowledge
import llobot.crammers.deletions
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
    deletion_crammer: DeletionCrammer = llobot.crammers.deletions.standard(),
    update_crammer: KnowledgeCrammer = llobot.crammers.knowledge.updates(),
    retrieval_crammer: KnowledgeCrammer = llobot.crammers.knowledge.retrieval(),
    knowledge_share: float = 1.0,
    # This share is directly occupied by examples. Examples however consume space also indirectly by forcing stuffing of updates.
    example_share: float = 0.2,
    retrieval_share: float = 1.0,
) -> Expert:
    if isinstance(relevance_scorer, KnowledgeSubset):
        relevance_scorer = llobot.scorers.knowledge.relevant(relevance_scorer)
    instructions = llobot.experts.instructions.coerce(instructions)
    knowledge_expert = llobot.experts.knowledge.standard(scope_scorer=scope_scorer, relevance_scorer=relevance_scorer, crammer=knowledge_crammer)
    example_expert = llobot.experts.examples.standard(crammer=example_crammer)
    updates_expert = llobot.experts.knowledge.updates(deletion_crammer=deletion_crammer, update_crammer=update_crammer)
    retrieval_expert = llobot.experts.knowledge.retrieval(scraper=retrieval_scraper, crammer=retrieval_crammer, scope_scorer=scope_scorer, relevance_scorer=relevance_scorer)
    def stuff(request: ExpertRequest) -> Context:
        # Budget distribution priorities: instructions, retrievals, examples, updates, knowledge.
        system = instructions(request)
        remaining_budget = request.budget - system.cost
        # Stuff retrievals first, because they are the highest priority for the user.
        retrieval_budget = min(remaining_budget, int(retrieval_share * request.budget))
        retrievals = retrieval_expert(request.replace(budget=retrieval_budget, context=request.context+system))
        remaining_budget -= retrievals.cost
        example_budget = min(remaining_budget, int(example_share * request.budget))
        examples = example_expert(request.replace(budget=example_budget, context=request.context+system))
        remaining_budget -= examples.cost
        # Compute updates after examples with all remaining budget.
        updates = updates_expert(request.replace(budget=remaining_budget, context=request.context+system+examples))
        # Stuff retrievals again, this time with examples and updates in the context to avoid document duplication.
        remaining_budget = request.budget - system.cost - examples.cost - updates.cost
        retrieval_budget = min(remaining_budget, int(retrieval_share * request.budget))
        retrievals = retrieval_expert(request.replace(budget=retrieval_budget, context=request.context+system+examples+updates))
        remaining_budget -= retrievals.cost
        knowledge_budget = min(remaining_budget, int(knowledge_share * request.budget))
        knowledge = knowledge_expert(request.replace(budget=knowledge_budget, context=request.context+system+examples+updates+retrievals))
        return system + knowledge + examples + updates + retrievals
    return llobot.experts.create(stuff)

__all__ = [
    'standard',
]

