from __future__ import annotations
from datetime import datetime
from functools import cache
from pathlib import Path
from typing import Iterable
from llobot.chats.archives import ChatArchive, standard_chat_archive
from llobot.chats.branches import ChatBranch
from llobot.chats.intents import ChatIntent
from llobot.commands.approve import ApproveCommand
from llobot.commands.chain import StepChain
from llobot.commands.custom import CustomStep
from llobot.commands.cutoff import CutoffCommand, ImplicitCutoffStep
from llobot.commands.knowledge import ProjectKnowledgeStep
from llobot.commands.project import ProjectCommand
from llobot.commands.retrievals import RetrievalStep, standard_retrieval_commands
from llobot.commands.unrecognized import UnrecognizedCommand
from llobot.crammers.indexes import IndexCrammer, standard_index_crammer
from llobot.crammers.knowledge import KnowledgeCrammer, standard_knowledge_crammer
from llobot.environments import Environment
from llobot.environments.commands import CommandsEnv
from llobot.environments.context import ContextEnv
from llobot.environments.cutoff import CutoffEnv
from llobot.environments.knowledge import KnowledgeEnv
from llobot.environments.projects import ProjectEnv
from llobot.environments.prompt import PromptEnv
from llobot.environments.replay import ReplayEnv
from llobot.environments.session import SessionEnv
from llobot.environments.status import StatusEnv
from llobot.formats.knowledge import KnowledgeFormat, standard_knowledge_format
from llobot.formats.mentions import parse_mentions
from llobot.formats.prompts import (
    PromptFormat,
    reminder_prompt_format,
    standard_prompt_format,
)
from llobot.fs import data_home
from llobot.fs.zones import Zoning
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
from llobot.memories.examples import ExampleMemory
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
    _name: str
    _model: Model
    _system: str
    _knowledge_archive: KnowledgeArchive
    _relevance_scorer: KnowledgeScorer
    _graph_scorer: KnowledgeScorer
    _ranker: KnowledgeRanker
    _knowledge_crammer: KnowledgeCrammer
    _index_crammer: IndexCrammer
    _knowledge_format: KnowledgeFormat
    _prompt_format: PromptFormat
    _reminder_format: PromptFormat
    _step_chain: StepChain
    _examples: ExampleMemory

    def __init__(self, name: str, model: Model, *,
        prompt: str | Prompt = editor_system_prompt(),
        projects: Iterable[Project] = (),
        knowledge_archive: KnowledgeArchive = standard_knowledge_archive(),
        example_archive: ChatArchive | Zoning | Path | str = standard_chat_archive(data_home()/'llobot/examples'),
        relevance_scorer: KnowledgeScorer | KnowledgeSubset = irrelevant_subset_scorer(),
        graph_scorer: KnowledgeScorer = standard_scorer(),
        ranker: KnowledgeRanker = standard_ranker(),
        knowledge_crammer: KnowledgeCrammer = standard_knowledge_crammer(),
        index_crammer: IndexCrammer = standard_index_crammer(),
        knowledge_format: KnowledgeFormat = standard_knowledge_format(),
        prompt_format: PromptFormat = standard_prompt_format(),
        reminder_format: PromptFormat = reminder_prompt_format(),
    ):
        """
        Creates a new editor role.
        """
        self._name = name
        self._model = model
        self._examples = ExampleMemory(name, archive=example_archive)
        self._system = str(prompt)
        self._knowledge_archive = knowledge_archive
        if isinstance(relevance_scorer, KnowledgeSubset):
            self._relevance_scorer = relevant_subset_scorer(relevance_scorer)
        else:
            self._relevance_scorer = relevance_scorer
        self._graph_scorer = graph_scorer
        self._ranker = ranker
        self._knowledge_crammer = knowledge_crammer
        self._index_crammer = index_crammer
        self._knowledge_format = knowledge_format
        self._prompt_format = prompt_format
        self._reminder_format = reminder_format
        self._step_chain = StepChain(
            ProjectCommand(list(projects)),
            CutoffCommand(),
            ImplicitCutoffStep(self._knowledge_archive),
            ProjectKnowledgeStep(self._knowledge_archive),
            CustomStep(self.stuff),
            standard_retrieval_commands(),
            RetrievalStep(self._knowledge_format),
            ApproveCommand(self._examples),
            UnrecognizedCommand(),
        )

    @property
    def name(self) -> str:
        return self._name

    def stuff(self, env: Environment):
        """
        Populates the context with system prompt, knowledge, and index.

        Args:
            env: The environment to populate.
        """
        context = env[ContextEnv]
        if context.messages:
            return

        knowledge = env[KnowledgeEnv].get()
        budget = self._model.context_budget

        # System prompt
        system_chat = self._prompt_format(self._system)
        context.add(system_chat)
        budget -= system_chat.cost

        # Knowledge scores
        scores = self._relevance_scorer(knowledge)
        blacklist = knowledge.keys() - scores.keys()
        scores = self._graph_scorer.rescore(knowledge, scores)
        scores -= blacklist

        # Index
        # Add background scores so nothing is omitted from index
        index_scores = scores | uniform_scores(knowledge.keys(), 0.001)
        index_chat = self._index_crammer(index_scores, budget)
        context.add(index_chat)
        budget -= index_chat.cost

        # Knowledge
        ranking = self._ranker(knowledge)
        knowledge_chat, _ = self._knowledge_crammer(knowledge, budget, scores, ranking)
        context.add(knowledge_chat)

    def chat(self, prompt: ChatBranch) -> ModelStream:
        env = Environment()
        context = env[ContextEnv]
        queue = env[CommandsEnv]
        prompt_env = env[PromptEnv]
        status_env = env[StatusEnv]

        for i, message in enumerate(prompt):
            if i + 1 == len(prompt):
                env[ReplayEnv].start_recording()

            if message.intent == ChatIntent.PROMPT:
                prompt_env.set(message.content)
                if i + 1 < len(prompt) and prompt[i + 1].intent == ChatIntent.SESSION:
                    queue.add(parse_mentions(prompt[i + 1]))
                queue.add(parse_mentions(message))
                self._step_chain.process(env)

            if i == 0:
                context.add(self._reminder_format(self._system))

            context.add(message)

        if status_env.populated:
            yield from status_env.stream()
            return

        session_env = env[SessionEnv]
        yield from session_env.stream()
        context.add(session_env.message())

        assembled_prompt = context.build()
        yield from self._model.generate(assembled_prompt)

__all__ = [
    'editor_system_prompt',
    'Editor',
]
