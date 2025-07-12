from __future__ import annotations
from functools import cache, lru_cache
from llobot.chats import ChatRole
from llobot.knowledge import Knowledge
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.scrapers import Scraper
from llobot.scorers.knowledge import KnowledgeScorer
from llobot.crammers.knowledge import KnowledgeCrammer
from llobot.crammers.deletions import DeletionCrammer
from llobot.crammers.examples import ExampleCrammer
from llobot.contexts import Context
from llobot.instructions import SystemPrompt
from llobot.roles import Role
from llobot.roles.requests import RoleRequest
import llobot.scrapers
import llobot.scorers.knowledge
import llobot.scores.knowledge
import llobot.crammers.knowledge
import llobot.crammers.deletions
import llobot.crammers.examples
import llobot.contexts
import llobot.instructions
import llobot.roles
import llobot.text
import llobot.links

@cache
def system() -> SystemPrompt:
    """
    Returns the standard system prompt for the editor role.
    """
    return llobot.instructions.prepare(
        llobot.instructions.read('editor.md'),
        *llobot.instructions.editing(),
        *llobot.instructions.answering(),
    )

@lru_cache
def create(*,
    instructions: str = system().compile(),
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
    example_share: float = 0.3,
    retrieval_share: float = 1.0,
) -> Role:
    """
    Creates a new editor role.
    """
    if isinstance(relevance_scorer, KnowledgeSubset):
        relevance_scorer = llobot.scorers.knowledge.relevant(relevance_scorer)

    def stuff(request: RoleRequest) -> Context:
        fresh_knowledge = request.project.root.knowledge(request.cutoff) if request.project else Knowledge()

        # Calculate relevance scores once
        relevance_scores = relevance_scorer(fresh_knowledge)
        if request.project and request.project.is_subproject:
            relevance_scores *= llobot.scores.knowledge.prioritize(fresh_knowledge, request.project.subset)

        # Find retrieval links once
        messages = (message.content for message in request.prompt if message.role == ChatRole.USER)
        prompt_text = llobot.text.concat(*messages)
        retrieved_links = llobot.links.resolve_best(retrieval_scraper.scrape_prompt(prompt_text), fresh_knowledge, relevance_scores)

        # --- System ---
        system = llobot.contexts.system(instructions)
        remaining_budget = request.budget - system.cost

        # --- Preliminary retrieval pass ---
        retrieval_budget = min(remaining_budget, int(retrieval_share * request.budget))
        retrievals = retrieval_crammer.cram(fresh_knowledge, retrieval_budget, llobot.scores.knowledge.coerce(retrieved_links), system)
        # This is the only use we have for preliminary retrievals: to calculate remaining budget for other parts of the context
        remaining_budget -= retrievals.cost

        # --- Examples ---
        example_budget = min(remaining_budget, int(example_share * request.budget))
        recent_examples = request.memory.recent_examples(request.project, request.cutoff)
        examples = example_crammer.cram(recent_examples, example_budget, system)
        remaining_budget -= examples.cost

        # --- Updates ---
        context_knowledge = (system + examples).knowledge
        deletions_index = context_knowledge.keys() - fresh_knowledge.keys()
        updates = deletion_crammer.cram(deletions_index, remaining_budget)
        updates += update_crammer.cram(fresh_knowledge, remaining_budget - updates.cost, llobot.scores.knowledge.coerce(context_knowledge.keys()), system + examples + updates)

        # --- Final retrieval pass ---
        remaining_budget = request.budget - system.cost - examples.cost - updates.cost
        retrieval_budget = min(remaining_budget, int(retrieval_share * request.budget))
        retrievals = retrieval_crammer.cram(fresh_knowledge, retrieval_budget, llobot.scores.knowledge.coerce(retrieved_links), system + examples + updates)
        remaining_budget -= retrievals.cost

        # --- Knowledge ---
        knowledge_budget = min(remaining_budget, int(knowledge_share * request.budget))
        knowledge = knowledge_crammer.cram(fresh_knowledge, knowledge_budget, relevance_scores, system + examples + updates + retrievals)

        return system + knowledge + examples + updates + retrievals
    return llobot.roles.create(stuff)

__all__ = [
    'system',
    'create',
]

