from __future__ import annotations
from functools import cache, lru_cache
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.scrapers import Scraper
from llobot.scorers.knowledge import KnowledgeScorer
from llobot.crammers.knowledge import KnowledgeCrammer
from llobot.crammers.deletions import DeletionCrammer
from llobot.crammers.examples import ExampleCrammer
from llobot.contexts import Context
from llobot.roles import Role
from llobot.roles.requests import RoleRequest
import llobot.scrapers
import llobot.scorers.knowledge
import llobot.crammers.knowledge
import llobot.crammers.deletions
import llobot.crammers.examples
import llobot.contexts
import llobot.instructions
import llobot.roles
import llobot.roles.knowledge
import llobot.roles.assistant

@cache
def description() -> str:
    return llobot.instructions.read('editor.md')

@cache
def instructions() -> str:
    return llobot.instructions.compile(
        description(),
        *llobot.instructions.editing(),
        *llobot.instructions.answering(),
    )

@lru_cache
def create(*,
    instructions: str = instructions(),
    retrieval_scraper: Scraper = llobot.scrapers.retrieval(),
    relevance_scorer: KnowledgeScorer | KnowledgeSubset = llobot.scorers.knowledge.irrelevant(),
    knowledge_crammer: KnowledgeCrammer = llobot.crammers.knowledge.standard(),
    example_crammer: ExampleCrammer = llobot.crammers.examples.standard(),
    deletion_crammer: DeletionCrammer = llobot.crammers.deletions.standard(),
    update_crammer: KnowledgeCrammer = llobot.crammers.knowledge.updates(),
    retrieval_crammer: KnowledgeCrammer = llobot.crammers.knowledge.retrieval(),
    knowledge_share: float = 1.0,
    # This share is directly occupied by examples.
    # Examples however consume space also indirectly by forcing stuffing of updates.
    example_share: float = 0.5,
    retrieval_share: float = 1.0,
) -> Role:
    if isinstance(relevance_scorer, KnowledgeSubset):
        relevance_scorer = llobot.scorers.knowledge.relevant(relevance_scorer)
    knowledge_role = llobot.roles.knowledge.create(relevance_scorer=relevance_scorer, crammer=knowledge_crammer)
    example_role = llobot.roles.assistant.create(crammer=example_crammer)
    updates_role = llobot.roles.knowledge.updates(deletion_crammer=deletion_crammer, update_crammer=update_crammer)
    retrieval_role = llobot.roles.knowledge.retrieval(scraper=retrieval_scraper, crammer=retrieval_crammer, relevance_scorer=relevance_scorer)
    def stuff(request: RoleRequest) -> Context:
        # Budget distribution priorities: instructions, retrievals, examples, updates, knowledge.
        system = llobot.contexts.system(instructions)
        remaining_budget = request.budget - system.cost
        # Stuff retrievals first, because they are the highest priority for the user.
        retrieval_budget = min(remaining_budget, int(retrieval_share * request.budget))
        retrievals = retrieval_role(request.replace(budget=retrieval_budget, context=request.context+system))
        remaining_budget -= retrievals.cost
        example_budget = min(remaining_budget, int(example_share * request.budget))
        examples = example_role(request.replace(budget=example_budget, context=request.context+system))
        remaining_budget -= examples.cost
        # Compute updates after examples with all remaining budget.
        updates = updates_role(request.replace(budget=remaining_budget, context=request.context+system+examples))
        # Stuff retrievals again, this time with examples and updates in the context to avoid document duplication.
        remaining_budget = request.budget - system.cost - examples.cost - updates.cost
        retrieval_budget = min(remaining_budget, int(retrieval_share * request.budget))
        retrievals = retrieval_role(request.replace(budget=retrieval_budget, context=request.context+system+examples+updates))
        remaining_budget -= retrievals.cost
        knowledge_budget = min(remaining_budget, int(knowledge_share * request.budget))
        knowledge = knowledge_role(request.replace(budget=knowledge_budget, context=request.context+system+examples+updates+retrievals))
        return system + knowledge + examples + updates + retrievals
    return llobot.roles.create(stuff)

__all__ = [
    'description',
    'instructions',
    'create',
]

