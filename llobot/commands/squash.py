"""
Squash command for saving knowledge delta as an example.
"""
from __future__ import annotations
from llobot.chats.branches import ChatBranch
from llobot.chats.intents import ChatIntent
from llobot.chats.messages import ChatMessage
from llobot.commands import Command
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.knowledge import KnowledgeEnv
from llobot.environments.projects import ProjectEnv
from llobot.environments.replay import ReplayEnv
from llobot.environments.status import StatusEnv
from llobot.formats.documents import DocumentFormat
from llobot.knowledge.deltas.diffs import knowledge_delta_between
from llobot.memories.examples import ExampleMemory

class SquashCommand(Command):
    """
    A command that computes the knowledge delta and saves it as an example.
    """
    _examples: ExampleMemory
    _document_format: DocumentFormat

    def __init__(self, examples: ExampleMemory, document_format: DocumentFormat):
        self._examples = examples
        self._document_format = document_format

    def handle(self, text: str, env: Environment) -> bool:
        if text != 'squash':
            return False

        if env[ReplayEnv].replaying():
            return True

        project = env[ProjectEnv].get()
        if not project:
            raise ValueError("Cannot squash without a project.")

        user_prompt_message = next((m for m in env[ContextEnv].messages if m.intent == ChatIntent.PROMPT), None)
        if user_prompt_message is None:
            raise ValueError("Cannot squash an empty conversation.")

        initial_knowledge = env[KnowledgeEnv].get()
        current_knowledge = project.load()

        delta = knowledge_delta_between(initial_knowledge, current_knowledge)
        if not delta:
            raise ValueError("No changes detected, nothing to squash.")

        response_content = self._document_format.render_all(delta)
        response_message = ChatMessage(ChatIntent.RESPONSE, response_content)
        example = ChatBranch([user_prompt_message, response_message])
        self._examples.save(example, env)

        env[StatusEnv].append("✅ Changes squashed and saved as an example.")
        return True

__all__ = [
    'SquashCommand',
]
