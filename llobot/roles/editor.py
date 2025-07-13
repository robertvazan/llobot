from __future__ import annotations
from functools import cache
from datetime import datetime
from llobot.chats import ChatBranch
from llobot.knowledge import Knowledge
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.scrapers import Scraper
from llobot.scorers.knowledge import KnowledgeScorer
from llobot.crammers.knowledge import KnowledgeCrammer
from llobot.crammers.deletions import DeletionCrammer
from llobot.crammers.examples import ExampleCrammer
from llobot.contexts import Context
from llobot.instructions import SystemPrompt
from llobot.projects import Project
from llobot.roles import Role
from llobot.roles.memory import RoleMemory
import llobot.scrapers
import llobot.scorers.knowledge
import llobot.scores.knowledge
import llobot.crammers.knowledge
import llobot.crammers.deletions
import llobot.crammers.examples
import llobot.contexts
import llobot.instructions
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

class Editor(Role):
    _instructions: str
    _retrieval_scraper: Scraper
    _relevance_scorer: KnowledgeScorer
    _knowledge_crammer: KnowledgeCrammer
    _example_crammer: ExampleCrammer
    _deletion_crammer: DeletionCrammer
    _update_crammer: KnowledgeCrammer
    _retrieval_crammer: KnowledgeCrammer
    _knowledge_share: float
    _example_share: float
    _retrieval_share: float

    def __init__(self, *,
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
    ):
        """
        Creates a new editor role.
        """
        self._instructions = instructions
        self._retrieval_scraper = retrieval_scraper
        if isinstance(relevance_scorer, KnowledgeSubset):
            self._relevance_scorer = llobot.scorers.knowledge.relevant(relevance_scorer)
        else:
            self._relevance_scorer = relevance_scorer
        self._knowledge_crammer = knowledge_crammer
        self._example_crammer = example_crammer
        self._deletion_crammer = deletion_crammer
        self._update_crammer = update_crammer
        self._retrieval_crammer = retrieval_crammer
        self._knowledge_share = knowledge_share
        self._example_share = example_share
        self._retrieval_share = retrieval_share

    def stuff(self, *,
        memory: RoleMemory,
        prompt: ChatBranch,
        project: Project | None,
        cutoff: datetime,
        budget: int,
    ) -> Context:
        fresh_knowledge = project.root.knowledge(cutoff) if project else Knowledge()

        # Calculate relevance scores once
        relevance_scores = self._relevance_scorer(fresh_knowledge)
        if project and project.is_subproject:
            relevance_scores *= llobot.scores.knowledge.prioritize(fresh_knowledge, project.subset)

        # Find retrieval links once
        retrieved_links = llobot.links.resolve_best(self._retrieval_scraper.scrape_prompt(prompt), fresh_knowledge, relevance_scores)

        # --- System ---
        system = llobot.contexts.system(self._instructions)
        remaining_budget = budget - system.cost

        # --- Preliminary retrieval pass ---
        retrieval_budget = min(remaining_budget, int(self._retrieval_share * budget))
        retrievals = self._retrieval_crammer.cram(fresh_knowledge, retrieval_budget, llobot.scores.knowledge.coerce(retrieved_links), system)
        # This is the only use we have for preliminary retrievals: to calculate remaining budget for other parts of the context
        remaining_budget -= retrievals.cost

        # --- Examples ---
        example_budget = min(remaining_budget, int(self._example_share * budget))
        recent_examples = memory.recent_examples(project, cutoff)
        examples = self._example_crammer.cram(recent_examples, example_budget, system)
        remaining_budget -= examples.cost

        # --- Updates ---
        context_knowledge = (system + examples).knowledge
        deletions_index = context_knowledge.keys() - fresh_knowledge.keys()
        updates = self._deletion_crammer.cram(deletions_index, remaining_budget)
        updates += self._update_crammer.cram(fresh_knowledge, remaining_budget - updates.cost, llobot.scores.knowledge.coerce(context_knowledge.keys()), system + examples + updates)

        # --- Final retrieval pass ---
        remaining_budget = budget - system.cost - examples.cost - updates.cost
        retrieval_budget = min(remaining_budget, int(self._retrieval_share * budget))
        retrievals = self._retrieval_crammer.cram(fresh_knowledge, retrieval_budget, llobot.scores.knowledge.coerce(retrieved_links), system + examples + updates)
        remaining_budget -= retrievals.cost

        # --- Knowledge ---
        knowledge_budget = min(remaining_budget, int(self._knowledge_share * budget))
        knowledge = self._knowledge_crammer.cram(fresh_knowledge, knowledge_budget, relevance_scores, system + examples + updates + retrievals)

        return system + knowledge + examples + updates + retrievals

__all__ = [
    'system',
    'Editor',
]

