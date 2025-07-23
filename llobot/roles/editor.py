from __future__ import annotations
from functools import cache
from datetime import datetime
from llobot.chats import ChatBranch, ChatBuilder, ChatIntent
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.knowledge.rankers import KnowledgeRanker
from llobot.scrapers import Scraper
from llobot.knowledge.scorers import KnowledgeScorer
from llobot.crammers.knowledge import KnowledgeCrammer
from llobot.crammers.edits import EditCrammer
from llobot.formatters.envelopes import EnvelopeFormatter
from llobot.formatters.knowledge import KnowledgeFormatter
from llobot.formatters.instructions import InstructionFormatter
from llobot.instructions import SystemPrompt
from llobot.projects import Project
from llobot.roles import Role
import llobot.scrapers
import llobot.knowledge.scorers
import llobot.knowledge.scores
import llobot.crammers.knowledge
import llobot.crammers.edits
import llobot.formatters.knowledge
import llobot.formatters.instructions
import llobot.formatters.envelopes
import llobot.instructions
import llobot.links
import llobot.knowledge.rankings
import llobot.knowledge.rankers
import llobot.knowledge.deltas

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
    _envelopes: EnvelopeFormatter
    _retrieval_formatter: KnowledgeFormatter
    _instruction_formatter: InstructionFormatter
    _example_share: float

    def __init__(self, name: str, *,
        instructions: str = system().compile(),
        retrieval_scraper: Scraper = llobot.scrapers.retrieval(),
        relevance_scorer: KnowledgeScorer | KnowledgeSubset = llobot.knowledge.scorers.irrelevant(),
        graph_scorer: KnowledgeScorer = llobot.knowledge.scorers.standard(),
        ranker: KnowledgeRanker = llobot.knowledge.rankers.standard(),
        knowledge_crammer: KnowledgeCrammer = llobot.crammers.knowledge.standard(),
        edit_crammer: EditCrammer = llobot.crammers.edits.standard(),
        envelopes: EnvelopeFormatter = llobot.formatters.envelopes.standard(),
        retrieval_formatter: KnowledgeFormatter = llobot.formatters.knowledge.standard(),
        instruction_formatter: InstructionFormatter = llobot.formatters.instructions.standard(),
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
            self._relevance_scorer = llobot.knowledge.scorers.relevant(relevance_scorer)
        else:
            self._relevance_scorer = relevance_scorer
        self._graph_scorer = graph_scorer
        self._ranker = ranker
        self._knowledge_crammer = knowledge_crammer
        self._edit_crammer = edit_crammer
        self._envelopes = envelopes
        self._retrieval_formatter = retrieval_formatter
        self._instruction_formatter = instruction_formatter
        self._example_share = example_share

    def stuff(self, *,
        prompt: ChatBranch,
        project: Project | None,
        cutoff: datetime,
        budget: int,
    ) -> ChatBranch:
        knowledge = project.root.knowledge(cutoff) if project else Knowledge()

        # 1. System instructions
        system_chat = self._instruction_formatter(self._instructions)
        budget -= system_chat.cost

        # 2. Examples with associated updates
        edit_budget = int(budget * self._example_share)
        recent_examples = self.recent_examples(project, cutoff)
        history_chat, history_paths = self._edit_crammer(recent_examples, knowledge, edit_budget)

        # 3. Knowledge
        # Knowledge budget is fixed regardless of how many examples there are. Fixed budget improves caching.
        knowledge_budget = budget - edit_budget
        ranking = self._ranker(knowledge)
        scores = self._relevance_scorer(knowledge)
        blacklist = knowledge.keys() - scores.keys()
        if project and project.is_subproject:
            scores *= llobot.knowledge.scores.prioritize(knowledge, project.subset)
        scores = self._graph_scorer.rescore(knowledge, scores)
        scores -= history_paths
        scores -= blacklist

        knowledge_chat, knowledge_paths = self._knowledge_crammer(knowledge, knowledge_budget, scores, ranking)

        # 4. Retrievals
        retrieved_links = llobot.links.resolve(self._retrieval_scraper.scrape_prompt(prompt), knowledge)
        retrieved_knowledge = (knowledge & retrieved_links) - (knowledge_paths | history_paths)
        retrievals_chat = self._retrieval_formatter.render_fresh(retrieved_knowledge, ranking)

        chat = ChatBuilder()
        chat.add(system_chat)
        chat.add(knowledge_chat)
        chat.add(history_chat)
        chat.add(retrievals_chat)
        return chat.build()

    def handle_ok(self, chat: ChatBranch, project: Project | None, cutoff: datetime):
        if not project:
            super().handle_ok(chat, project, cutoff)
            return

        edit_delta = self._envelopes.parse_chat(chat[1:])
        if not edit_delta:
            super().handle_ok(chat, project, cutoff)
            return

        project.root.refresh()
        initial_knowledge = project.root.knowledge(cutoff)
        current_knowledge = project.root.knowledge()
        delta = llobot.knowledge.deltas.between(initial_knowledge, current_knowledge, move_hints=edit_delta.moves)

        compressed_delta = llobot.knowledge.deltas.diff_compress(initial_knowledge, delta)
        response_content = self._envelopes.format_all(compressed_delta)
        synthetic_response = ChatIntent.RESPONSE.message(response_content)
        example_chat = chat[0].branch() + synthetic_response

        self.save_example(example_chat, project)

__all__ = [
    'system',
    'Editor',
]
