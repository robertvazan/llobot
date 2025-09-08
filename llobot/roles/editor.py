from __future__ import annotations
from datetime import datetime
from functools import cache
from typing import Iterable
from llobot.chats.branches import ChatBranch
from llobot.chats.intents import ChatIntent
from llobot.commands.chain import StepChain
from llobot.commands.custom import CustomStep
from llobot.commands.cutoff import CutoffCommand, ImplicitCutoffStep
from llobot.commands.knowledge import ProjectKnowledgeStep
from llobot.commands.project import ProjectCommand
from llobot.commands.retrievals import RetrievalStep
from llobot.commands.retrievals.solo import SoloRetrievalCommand
from llobot.commands.unrecognized import UnrecognizedCommand
from llobot.crammers.edits import EditCrammer, standard_edit_crammer
from llobot.crammers.indexes import IndexCrammer, standard_index_crammer
from llobot.crammers.knowledge import KnowledgeCrammer, standard_knowledge_crammer
from llobot.environments import Environment
from llobot.environments.commands import CommandsEnv
from llobot.environments.context import ContextEnv
from llobot.environments.cutoff import CutoffEnv
from llobot.environments.knowledge import KnowledgeEnv
from llobot.environments.projects import ProjectEnv
from llobot.environments.replay import ReplayEnv
from llobot.environments.session import SessionEnv
from llobot.formats.documents import DocumentFormat
from llobot.formats.knowledge import KnowledgeFormat, standard_knowledge_format
from llobot.formats.mentions import parse_mentions
from llobot.formats.prompts import (
    PromptFormat,
    reminder_prompt_format,
    standard_prompt_format,
)
from llobot.knowledge.archives import KnowledgeArchive, standard_knowledge_archive
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
    _knowledge_archive: KnowledgeArchive
    _relevance_scorer: KnowledgeScorer
    _graph_scorer: KnowledgeScorer
    _ranker: KnowledgeRanker
    _knowledge_crammer: KnowledgeCrammer
    _edit_crammer: EditCrammer
    _index_crammer: IndexCrammer
    _document_format: DocumentFormat
    _knowledge_format: KnowledgeFormat
    _prompt_format: PromptFormat
    _reminder_format: PromptFormat
    _example_share: float
    _step_chain: StepChain

    def __init__(self, name: str, model: Model, *,
        prompt: str | Prompt = editor_system_prompt(),
        projects: Iterable[Project] = (),
        knowledge_archive: KnowledgeArchive = standard_knowledge_archive(),
        relevance_scorer: KnowledgeScorer | KnowledgeSubset = irrelevant_subset_scorer(),
        graph_scorer: KnowledgeScorer = standard_scorer(),
        ranker: KnowledgeRanker = standard_ranker(),
        knowledge_crammer: KnowledgeCrammer = standard_knowledge_crammer(),
        edit_crammer: EditCrammer = standard_edit_crammer(),
        index_crammer: IndexCrammer = standard_index_crammer(),
        knowledge_format: KnowledgeFormat = standard_knowledge_format(),
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
        self._knowledge_archive = knowledge_archive
        if isinstance(relevance_scorer, KnowledgeSubset):
            self._relevance_scorer = relevant_subset_scorer(relevance_scorer)
        else:
            self._relevance_scorer = relevance_scorer
        self._graph_scorer = graph_scorer
        self._ranker = ranker
        self._knowledge_crammer = knowledge_crammer
        self._edit_crammer = edit_crammer
        self._index_crammer = index_crammer
        self._knowledge_format = knowledge_format
        self._document_format = knowledge_format.document_format
        self._prompt_format = prompt_format
        self._reminder_format = reminder_format
        self._example_share = example_share
        self._step_chain = StepChain(
            ProjectCommand(list(projects)),
            CutoffCommand(),
            ImplicitCutoffStep(self._knowledge_archive),
            ProjectKnowledgeStep(self._knowledge_archive),
            CustomStep(self.stuff),
            SoloRetrievalCommand(),
            RetrievalStep(self._knowledge_format),
            UnrecognizedCommand(),
        )

    def stuff(self, env: Environment):
        """
        Populates the context with system prompt, knowledge, and examples.

        Args:
            env: The environment to populate.
        """
        context = env[ContextEnv]
        if context.messages:
            return

        project = env[ProjectEnv].get()
        knowledge = env[KnowledgeEnv].get()
        cutoff = env[CutoffEnv].get()
        budget = self.model.context_budget

        # System prompt
        system_chat = self._prompt_format(self._system)
        context.add(system_chat)
        budget -= system_chat.cost

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
        knowledge_chat, _ = self._knowledge_crammer(knowledge, knowledge_budget, scores, ranking)

        context.add(index_chat)
        context.add(knowledge_chat)
        context.add(history_chat)

    def chat(self, prompt: ChatBranch) -> ModelStream:
        env = Environment()
        context = env[ContextEnv]
        queue = env[CommandsEnv]

        for i, message in enumerate(prompt):
            if i + 1 == len(prompt):
                env[ReplayEnv].start_recording()

            if message.intent == ChatIntent.PROMPT:
                if i + 1 < len(prompt) and prompt[i + 1].intent == ChatIntent.SESSION:
                    queue.add(parse_mentions(prompt[i + 1]))
                queue.add(parse_mentions(message))
                self._step_chain.process(env)

            if i == 0:
                context.add(self._reminder_format(self._system))

            context.add(message)

        session_env = env[SessionEnv]
        yield from session_env.stream()
        context.add(session_env.message())

        assembled_prompt = context.build()
        yield from self.model.generate(assembled_prompt)

    # def handle_ok(self, chat: ChatBranch, cutoff: datetime):
    #     env = Environment()
    #     self._step_chain.process_chat(chat, env)
    #     project = env[ProjectEnv].get()

    #     if not project:
    #         self.save_example(chat, None)
    #         return

    #     self._knowledge_archive.refresh(project.name, project)
    #     initial_knowledge = self._knowledge_archive.last(project.name, cutoff)
    #     current_knowledge = self._knowledge_archive.last(project.name)
    #     delta = knowledge_delta_between(initial_knowledge, current_knowledge)

    #     compressed_delta = diff_compress_knowledge(initial_knowledge, delta)
    #     response_content = self._document_format.render_all(compressed_delta)
    #     synthetic_response = ChatMessage(ChatIntent.RESPONSE, response_content)
    #     example_chat = ChatBranch([chat[0]]) + synthetic_response

    #     self.save_example(example_chat, project)

__all__ = [
    'editor_system_prompt',
    'Editor',
]
