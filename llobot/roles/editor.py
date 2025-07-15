from __future__ import annotations
from functools import cache
from datetime import datetime
from llobot.chats import ChatBranch
from llobot.knowledge import Knowledge
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.scrapers import Scraper
from llobot.scorers.knowledge import KnowledgeScorer
from llobot.crammers.knowledge import KnowledgeCrammer
from llobot.crammers.edits import EditCrammer
from llobot.contexts import Context
from llobot.instructions import SystemPrompt
from llobot.projects import Project
from llobot.roles import Role
import llobot.scrapers
import llobot.scorers.knowledge
import llobot.scores.knowledge
import llobot.crammers.knowledge
import llobot.crammers.edits
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
    _edit_crammer: EditCrammer
    _retrieval_crammer: KnowledgeCrammer
    _knowledge_share: float
    _example_share: float
    _retrieval_share: float

    def __init__(self, name: str, *,
        instructions: str = system().compile(),
        retrieval_scraper: Scraper = llobot.scrapers.retrieval(),
        relevance_scorer: KnowledgeScorer | KnowledgeSubset = llobot.scorers.knowledge.irrelevant(),
        knowledge_crammer: KnowledgeCrammer = llobot.crammers.knowledge.standard(),
        edit_crammer: EditCrammer = llobot.crammers.edits.standard(),
        retrieval_crammer: KnowledgeCrammer = llobot.crammers.knowledge.retrieval(),
        knowledge_share: float = 1.0,
        # Share of the context dedicated to examples and associated knowledge updates.
        example_share: float = 0.4,
        retrieval_share: float = 1.0,
        **kwargs,
    ):
        """
        Creates a new editor role.
        """
        super().__init__(name, **kwargs)
        self._instructions = instructions
        self._retrieval_scraper = retrieval_scraper
        if isinstance(relevance_scorer, KnowledgeSubset):
            self._relevance_scorer = llobot.scorers.knowledge.relevant(relevance_scorer)
        else:
            self._relevance_scorer = relevance_scorer
        self._knowledge_crammer = knowledge_crammer
        self._edit_crammer = edit_crammer
        self._retrieval_crammer = retrieval_crammer
        self._knowledge_share = knowledge_share
        self._example_share = example_share
        self._retrieval_share = retrieval_share

    def stuff(self, *,
        prompt: ChatBranch,
        project: Project | None,
        cutoff: datetime,
        budget: int,
    ) -> Context:
        fresh_knowledge = project.root.knowledge(cutoff) if project else Knowledge()

        # Find retrieval links once
        retrieved_links = llobot.links.resolve(self._retrieval_scraper.scrape_prompt(prompt), fresh_knowledge)

        # --- System ---
        system = llobot.contexts.system(self._instructions)
        remaining_budget = budget - system.cost

        # --- Preliminary retrieval pass ---
        retrieval_budget = min(remaining_budget, int(self._retrieval_share * budget))
        retrievals = self._retrieval_crammer.cram(fresh_knowledge, retrieval_budget, llobot.scores.knowledge.coerce(retrieved_links), system)
        # This is the only use we have for preliminary retrievals: to calculate remaining budget for other parts of the context
        remaining_budget -= retrievals.cost

        # --- Examples with associated updates ---
        edit_budget = min(remaining_budget, int(self._example_share * budget))
        recent_examples = self.recent_examples(project, cutoff)
        edits = self._edit_crammer.cram(recent_examples, fresh_knowledge, edit_budget)
        remaining_budget -= edits.cost

        # --- Final retrieval pass ---
        remaining_budget = budget - system.cost - edits.cost
        retrieval_budget = min(remaining_budget, int(self._retrieval_share * budget))
        retrievals = self._retrieval_crammer.cram(fresh_knowledge, retrieval_budget, llobot.scores.knowledge.coerce(retrieved_links), system + edits)
        remaining_budget -= retrievals.cost

        # --- Knowledge ---
        knowledge_budget = min(remaining_budget, int(self._knowledge_share * budget))
        relevance_scores = self._relevance_scorer(fresh_knowledge)
        if project and project.is_subproject:
            relevance_scores *= llobot.scores.knowledge.prioritize(fresh_knowledge, project.subset)
        knowledge = self._knowledge_crammer.cram(fresh_knowledge, knowledge_budget, relevance_scores, system + edits + retrievals)

        return system + knowledge + edits + retrievals

__all__ = [
    'system',
    'Editor',
]
