"""
Approve command for saving examples.
"""
from __future__ import annotations
from llobot.chats.thread import ChatThread
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.commands import handle_commands
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.prompt import PromptEnv
from llobot.environments.status import StatusEnv
from llobot.formats.mentions import strip_mentions
from llobot.memories.examples import ExampleMemory

def handle_approve_command(text: str, env: Environment, examples: ExampleMemory) -> bool:
    """
    A command to approve the last interaction and save it as an example.
    """
    if text != 'approve':
        return False

    context = env[ContextEnv]
    prompt_env = env[PromptEnv]

    user_prompt_message = next((m for m in context.build() if m.intent == ChatIntent.PROMPT), None)
    if user_prompt_message is None:
        raise ValueError("Cannot approve an empty conversation.")

    prompt_text = prompt_env.get()
    response_text = strip_mentions(prompt_text)
    if response_text:
        response_message = ChatMessage(ChatIntent.RESPONSE, response_text)
        example = ChatThread([user_prompt_message, response_message])
    else:
        # Fallback if stripped response is empty or prompt was not set.
        messages = [m for m in context.build() if m.intent in [ChatIntent.PROMPT, ChatIntent.RESPONSE]]
        example = ChatThread(messages)

    examples.save(example, env)
    env[StatusEnv].append("✅ Example saved.")

    return True

def handle_approve_commands(env: Environment, examples: ExampleMemory):
    """
    Handles `@approve` commands in the environment.
    """
    handle_commands(env, lambda text, env: handle_approve_command(text, env, examples))

__all__ = [
    'handle_approve_command',
    'handle_approve_commands',
]
