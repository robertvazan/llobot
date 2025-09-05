from __future__ import annotations
from datetime import datetime
from functools import cache
from llobot.chats.branches import ChatBranch
from llobot.chats.builders import ChatBuilder
from llobot.chats.intents import ChatIntent
from llobot.chats.messages import ChatMessage
from llobot.commands.chains import CommandChain
from llobot.commands.cutoffs import CutoffCommand
from llobot.commands.projects import ProjectCommand
from llobot.commands.retrievals import RetrievalCommand
from llobot.crammers.edits import EditCrammer, standard_edit_crammer
from llobot.crammers.indexes import IndexCrammer, standard_index_crammer
from llobot.crammers.knowledge import KnowledgeCrammer, standard_knowledge_crammer
from llobot.environments import Environment
from llobot.environments.cutoffs import CutoffEnv
from llobot.environments.knowledge import KnowledgeEnv
from llobot.environments.projects import ProjectEnv
from llobot.environments.retrievals import RetrievalsEnv
from llobot.environments.session_messages import SessionMessageEnv
from llobot.formats.deltas import DeltaFormat, standard_delta_format
from llobot.formats.knowledge import KnowledgeFormat, standard_knowledge_format
from llobot.formats.prompts import (
    PromptFormat,
    reminder_prompt_format,
    standard_prompt_format,
)
from llobot.knowledge import Knowledge
from llobot.knowledge.deltas import diff_compress_knowledge, knowledge_delta_between
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.rankers import KnowledgeRanker, standard_ranker
from llobot.knowledge.scorers import (
    KnowledgeScorer,
    irrelevant_subset_scorer,
    relevant_subset_scorer,
    standard_scorer,
)
from llobot.knowledge.scores import uniform_scores
from llobot.knowledge.subsets import KnowledgeSubset
from llobot.models import Model
from llobot.models.streams import ModelStream
from llobot.projects import Project
from llobot.prompts import (
    Prompt,
    SystemPrompt,
    answering_prompt_section,
    editing_prompt_section,
    read_prompt,
)
from llobot.roles import Role

@cache
def editor_system_prompt() -> SystemPrompt:
    """
    Returns the standard system prompt for the editor role.
    """
    return SystemPrompt(
        read_prompt('editor.md'),
        editing_prompt_section(),
        answering_prompt_section(),
    )

class Editor(Role):
    _system: str
    _relevance_scorer: KnowledgeScorer
    _graph_scorer: KnowledgeScorer
    _ranker: KnowledgeRanker
    _knowledge_crammer: KnowledgeCrammer
    _edit_crammer: EditCrammer
    _index_crammer: IndexCrammer
    _delta_format: DeltaFormat
    _retrieval_format: KnowledgeFormat
    _prompt_format: PromptFormat
    _reminder_format: PromptFormat
    _example_share: float
    _command_chain: CommandChain

    def __init__(self, name: str, model: Model, *,
        prompt: str | Prompt = editor_system_prompt(),
        projects: list[Project] | None = None,
        relevance_scorer: KnowledgeScorer | KnowledgeSubset = irrelevant_subset_scorer(),
        graph_scorer: KnowledgeScorer = standard_scorer(),
        ranker: KnowledgeRanker = standard_ranker(),
        knowledge_crammer: KnowledgeCrammer = standard_knowledge_crammer(),
        edit_crammer: EditCrammer = standard_edit_crammer(),
        index_crammer: IndexCrammer = standard_index_crammer(),
        delta_format: DeltaFormat = standard_delta_format(),
        retrieval_format: KnowledgeFormat = standard_knowledge_format(),
        prompt_format: PromptFormat = standard_prompt_format(),
        reminder_format: PromptFormat = reminder_prompt_format(),
        # Share of the context dedicated to examples and associated knowledge updates.
        example_share: float = 0.4,
        **kwargs,
    ):
        """
        Creates a new editor role.
        """
        super().__init__(name, model, **kwargs)
        self._system = str(prompt)
        if isinstance(relevance_scorer, KnowledgeSubset):
            self._relevance_scorer = relevant_subset_scorer(relevance_scorer)
        else:
            self._relevance_scorer = relevance_scorer
        self._graph_scorer = graph_scorer
        self._ranker = ranker
        self._knowledge_crammer = knowledge_crammer
        self._edit_crammer = edit_crammer
        self._index_crammer = index_crammer
        self._delta_format = delta_format
        self._retrieval_format = retrieval_format
        self._prompt_format = prompt_format
        self._reminder_format = reminder_format
        self._example_share = example_share
        self._command_chain = CommandChain(ProjectCommand(projects), RetrievalCommand(), CutoffCommand())

    def chat(self, prompt: ChatBranch) -> ModelStream:
        env = Environment()
        self._command_chain.handle_chat(prompt, env)
        project = env[ProjectEnv].get()
        knowledge = env[KnowledgeEnv].get()
        cutoff = env[CutoffEnv].get()
        budget = self.model.context_budget

        # System prompt
        system_chat = self._prompt_format(self._system)
        budget -= system_chat.cost

        # Reminder
        reminder_chat = self._reminder_format(self._system)
        budget -= reminder_chat.cost

        # Examples with associated updates
        history_budget = int(budget * self._example_share)
        recent_examples = self.recent_examples(project, cutoff)
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
        index_scores = scores | uniform_scores(knowledge.keys(), 0.001)
        index_chat = self._index_crammer(index_scores, index_budget)

        # Knowledge
        knowledge_budget = index_budget - index_chat.cost
        ranking = self._ranker(knowledge)
        knowledge_chat, knowledge_paths = self._knowledge_crammer(knowledge, knowledge_budget, scores, ranking)

        # Retrievals
        retrieved_paths = env[RetrievalsEnv].get()
        retrieved_knowledge = (knowledge & retrieved_paths) - (knowledge_paths | history_paths)
        retrievals_chat = self._retrieval_format.render_fresh(retrieved_knowledge, ranking)

        builder = ChatBuilder()
        builder.add(system_chat)
        builder.add(index_chat)
        builder.add(knowledge_chat)
        builder.add(history_chat)
        builder.add(retrievals_chat)
        builder.add(reminder_chat)

        context = builder.build()
        assembled_prompt = context + prompt
        yield from env[SessionMessageEnv].stream()
        yield from self.model.generate(assembled_prompt)

    def handle_ok(self, chat: ChatBranch, cutoff: datetime):
        env = Environment()
        self._command_chain.handle_chat(chat, env)
        project = env[ProjectEnv].get()

        if not project:
            self.save_example(chat, None)
            return

        edit_delta = self._delta_format.parse_chat(chat[1:])
        if not edit_delta:
            self.save_example(chat, project)
            return

        project.refresh()
        initial_knowledge = project.knowledge(cutoff)
        current_knowledge = project.knowledge()
        delta = knowledge_delta_between(initial_knowledge, current_knowledge, move_hints=edit_delta.moves)

        compressed_delta = diff_compress_knowledge(initial_knowledge, delta)
        response_content = self._delta_format.render_all(compressed_delta)
        synthetic_response = ChatMessage(ChatIntent.RESPONSE, response_content)
        example_chat = chat[0].branch() + synthetic_response

        self.save_example(example_chat, project)

__all__ = [
    'editor_system_prompt',
    'Editor',
]
