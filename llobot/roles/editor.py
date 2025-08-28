from __future__ import annotations
from functools import cache
from datetime import datetime
from llobot.chats import ChatBranch, ChatBuilder, ChatIntent
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.knowledge.rankers import KnowledgeRanker
from llobot.knowledge.retrievals import RetrievalScraper
from llobot.knowledge.scorers import KnowledgeScorer
from llobot.crammers.knowledge import KnowledgeCrammer
from llobot.crammers.edits import EditCrammer
from llobot.crammers.indexes import IndexCrammer
from llobot.formatters.envelopes import EnvelopeFormatter
from llobot.formatters.knowledge import KnowledgeFormatter
from llobot.formatters.prompts import PromptFormatter
from llobot.prompts import SystemPrompt, Prompt
from llobot.projects import Project
from llobot.roles import Role
from llobot.models import Model
import llobot.knowledge.retrievals
import llobot.knowledge.scorers
import llobot.knowledge.scores
import llobot.crammers.knowledge
import llobot.crammers.edits
import llobot.crammers.indexes
import llobot.formatters.knowledge
import llobot.formatters.prompts
import llobot.formatters.envelopes
import llobot.prompts
import llobot.knowledge.rankings
import llobot.knowledge.rankers
import llobot.knowledge.deltas

@cache
def system() -> SystemPrompt:
    """
    Returns the standard system prompt for the editor role.
    """
    return SystemPrompt(
        llobot.prompts.read('editor.md'),
        llobot.prompts.editing(),
        llobot.prompts.answering(),
    )

class Editor(Role):
    _prompt: str
    _retrieval_scraper: RetrievalScraper
    _relevance_scorer: KnowledgeScorer
    _graph_scorer: KnowledgeScorer
    _ranker: KnowledgeRanker
    _knowledge_crammer: KnowledgeCrammer
    _edit_crammer: EditCrammer
    _index_crammer: IndexCrammer
    _envelopes: EnvelopeFormatter
    _retrieval_formatter: KnowledgeFormatter
    _prompt_formatter: PromptFormatter
    _reminder_formatter: PromptFormatter
    _example_share: float

    def __init__(self, name: str, model: Model, *,
        prompt: str | Prompt = system(),
        retrieval_scraper: RetrievalScraper = llobot.knowledge.retrievals.standard(),
        relevance_scorer: KnowledgeScorer | KnowledgeSubset = llobot.knowledge.scorers.irrelevant(),
        graph_scorer: KnowledgeScorer = llobot.knowledge.scorers.standard(),
        ranker: KnowledgeRanker = llobot.knowledge.rankers.standard(),
        knowledge_crammer: KnowledgeCrammer = llobot.crammers.knowledge.standard(),
        edit_crammer: EditCrammer = llobot.crammers.edits.standard(),
        index_crammer: IndexCrammer = llobot.crammers.indexes.standard(),
        envelopes: EnvelopeFormatter = llobot.formatters.envelopes.standard(),
        retrieval_formatter: KnowledgeFormatter = llobot.formatters.knowledge.standard(),
        prompt_formatter: PromptFormatter = llobot.formatters.prompts.standard(),
        reminder_formatter: PromptFormatter = llobot.formatters.prompts.reminder(),
        # Share of the context dedicated to examples and associated knowledge updates.
        example_share: float = 0.4,
        **kwargs,
    ):
        """
        Creates a new editor role.
        """
        super().__init__(name, model, **kwargs)
        self._prompt = str(prompt)
        self._retrieval_scraper = retrieval_scraper
        if isinstance(relevance_scorer, KnowledgeSubset):
            self._relevance_scorer = llobot.knowledge.scorers.relevant(relevance_scorer)
        else:
            self._relevance_scorer = relevance_scorer
        self._graph_scorer = graph_scorer
        self._ranker = ranker
        self._knowledge_crammer = knowledge_crammer
        self._edit_crammer = edit_crammer
        self._index_crammer = index_crammer
        self._envelopes = envelopes
        self._retrieval_formatter = retrieval_formatter
        self._prompt_formatter = prompt_formatter
        self._reminder_formatter = reminder_formatter
        self._example_share = example_share

    def stuff(self, *,
        prompt: ChatBranch,
        project: Project | None,
    ) -> ChatBranch:
        budget = self.model.context_budget
        knowledge = project.knowledge() if project else Knowledge()

        # System prompt
        system_chat = self._prompt_formatter(self._prompt)
        budget -= system_chat.cost

        # Reminder
        reminder_chat = self._reminder_formatter(self._prompt)
        budget -= reminder_chat.cost

        # Examples with associated updates
        history_budget = int(budget * self._example_share)
        recent_examples = self.recent_examples(project)
        history_chat, history_paths = self._edit_crammer(recent_examples, knowledge, history_budget)

        # Knowledge scores
        scores = self._relevance_scorer(knowledge)
        blacklist = knowledge.keys() - scores.keys()
        scores = self._graph_scorer.rescore(knowledge, scores)
        scores -= history_paths
        scores -= blacklist

        # Index
        index_budget = budget - history_chat.cost
        # Add background scores so nothing is omitted from index
        index_scores = scores | llobot.knowledge.scores.uniform(knowledge.keys(), 0.001)
        index_chat = self._index_crammer(index_scores, index_budget)

        # Knowledge
        knowledge_budget = index_budget - index_chat.cost
        ranking = self._ranker(knowledge)
        knowledge_chat, knowledge_paths = self._knowledge_crammer(knowledge, knowledge_budget, scores, ranking)

        # Retrievals
        retrieved_paths = self._retrieval_scraper(prompt, knowledge.keys())
        retrieved_knowledge = (knowledge & retrieved_paths) - (knowledge_paths | history_paths)
        retrievals_chat = self._retrieval_formatter.render_fresh(retrieved_knowledge, ranking)

        chat = ChatBuilder()
        chat.add(system_chat)
        chat.add(index_chat)
        chat.add(knowledge_chat)
        chat.add(history_chat)
        chat.add(retrievals_chat)
        chat.add(reminder_chat)

        return chat.build()

    def handle_ok(self, chat: ChatBranch, project: Project | None, cutoff: datetime):
        if not project:
            super().handle_ok(chat, project, cutoff)
            return

        edit_delta = self._envelopes.parse_chat(chat[1:])
        if not edit_delta:
            super().handle_ok(chat, project, cutoff)
            return

        project.refresh()
        initial_knowledge = project.knowledge(cutoff)
        current_knowledge = project.knowledge()
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
