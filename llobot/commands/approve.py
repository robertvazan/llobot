"""
Approve command for saving examples.
"""
from __future__ import annotations
from llobot.chats.branches import ChatBranch
from llobot.chats.intents import ChatIntent
from llobot.chats.messages import ChatMessage
from llobot.commands import Command
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.prompt import PromptEnv
from llobot.environments.status import StatusEnv
from llobot.formats.mentions import strip_mentions
from llobot.memories.examples import ExampleMemory

class ApproveCommand(Command):
    """
    A command to approve the last interaction and save it as an example.
    """
    _examples: ExampleMemory

    def __init__(self, examples: ExampleMemory):
        self._examples = examples

    def handle(self, text: str, env: Environment) -> bool:
        if text != 'approve':
            return False

        if not env[PromptEnv].is_last:
            return True

        context = env[ContextEnv]
        prompt_env = env[PromptEnv]

        user_prompt_message = next((m for m in context.build() if m.intent == ChatIntent.PROMPT), None)
        if user_prompt_message is None:
            raise ValueError("Cannot approve an empty conversation.")

        prompt_text = prompt_env.get()
        response_text = strip_mentions(prompt_text)
        if response_text:
            response_message = ChatMessage(ChatIntent.RESPONSE, response_text)
            example = ChatBranch([user_prompt_message, response_message])
        else:
            # Fallback if stripped response is empty or prompt was not set.
            messages = [m for m in context.build() if m.intent in [ChatIntent.PROMPT, ChatIntent.RESPONSE]]
            example = ChatBranch(messages)

        self._examples.save(example, env)
        env[StatusEnv].append("✅ Example saved.")

        return True

__all__ = [
    'ApproveCommand',
]
