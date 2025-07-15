from __future__ import annotations
from functools import cache
from datetime import datetime
from llobot.chats import ChatBranch
from llobot.knowledge import Knowledge
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.knowledge.rankers import KnowledgeRanker
from llobot.scrapers import Scraper
from llobot.scorers.knowledge import KnowledgeScorer
from llobot.crammers.knowledge import KnowledgeCrammer
from llobot.crammers.edits import EditCrammer
from llobot.formatters.knowledge import KnowledgeFormatter
from llobot.contexts import Context
from llobot.instructions import SystemPrompt
from llobot.projects import Project
from llobot.roles import Role
import llobot.scrapers
import llobot.scorers.knowledge
import llobot.scores.knowledge
import llobot.crammers.knowledge
import llobot.crammers.edits
import llobot.formatters.knowledge
import llobot.contexts
import llobot.instructions
import llobot.links
import llobot.knowledge.rankings
import llobot.knowledge.rankers

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
    _graph_scorer: KnowledgeScorer
    _ranker: KnowledgeRanker
    _knowledge_crammer: KnowledgeCrammer
    _edit_crammer: EditCrammer
    _retrieval_formatter: KnowledgeFormatter
    _example_share: float

    def __init__(self, name: str, *,
        instructions: str = system().compile(),
        retrieval_scraper: Scraper = llobot.scrapers.retrieval(),
        relevance_scorer: KnowledgeScorer | KnowledgeSubset = llobot.scorers.knowledge.irrelevant(),
        graph_scorer: KnowledgeScorer = llobot.scorers.knowledge.standard(),
        ranker: KnowledgeRanker = llobot.knowledge.rankers.standard(),
        knowledge_crammer: KnowledgeCrammer = llobot.crammers.knowledge.standard(),
        edit_crammer: EditCrammer = llobot.crammers.edits.standard(),
        retrieval_formatter: KnowledgeFormatter = llobot.formatters.knowledge.standard(),
        # Share of the context dedicated to examples and associated knowledge updates.
        example_share: float = 0.4,
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
        self._graph_scorer = graph_scorer
        self._ranker = ranker
        self._knowledge_crammer = knowledge_crammer
        self._edit_crammer = edit_crammer
        self._retrieval_formatter = retrieval_formatter
        self._example_share = example_share

    def stuff(self, *,
        prompt: ChatBranch,
        project: Project | None,
        cutoff: datetime,
        budget: int,
    ) -> Context:
        knowledge = project.root.knowledge(cutoff) if project else Knowledge()

        system = llobot.contexts.system(self._instructions)
        budget -= system.cost

        # Examples with associated updates
        edit_budget = int(budget * self._example_share)
        recent_examples = self.recent_examples(project, cutoff)
        history = self._edit_crammer(recent_examples, knowledge, edit_budget)

        # Knowledge
        knowledge_budget = budget - edit_budget
        ranking = self._ranker(knowledge)
        scores = self._relevance_scorer(knowledge)
        if project and project.is_subproject:
            scores *= llobot.scores.knowledge.prioritize(knowledge, project.subset)
        scores = self._graph_scorer.rescore(knowledge, scores)
        scores -= history.knowledge.keys()
        core = self._knowledge_crammer(knowledge, knowledge_budget, scores, ranking)

        # Retrievals
        retrieved_links = llobot.links.resolve(self._retrieval_scraper.scrape_prompt(prompt), knowledge)
        retrieved_knowledge = (knowledge & retrieved_links) - (core + history).knowledge.keys()
        retrievals = self._retrieval_formatter(retrieved_knowledge, ranking)

        return system + core + history + retrievals

__all__ = [
    'system',
    'Editor',
]
