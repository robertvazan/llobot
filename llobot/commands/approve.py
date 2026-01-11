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
from llobot.formats.mentions import strip_mentions
from llobot.memories.examples import ExampleMemory

def handle_approve_command(text: str, env: Environment, examples: ExampleMemory) -> bool:
    """
    A command to approve a correct prompt–response pair and save it as an example.

    Only the initial prompt and the last response are saved. Intermediate
    messages are not saved, so the user can iterate on refinements. If the
    command is accompanied by text, that text is taken to be the correct response.
    """
    if text != 'approve':
        return False

    prompt_env = env[PromptEnv]
    full_prompt = prompt_env.full

    initial_prompt = next((m for m in full_prompt if m.intent == ChatIntent.PROMPT), None)
    if initial_prompt is None:
        raise ValueError("Cannot approve an empty conversation.")

    command_message_text = prompt_env.current
    response_text = strip_mentions(command_message_text)
    if response_text:
        response_message = ChatMessage(ChatIntent.RESPONSE, response_text)
    else:
        prior_responses = [m for m in full_prompt[:-1] if m.intent == ChatIntent.RESPONSE]
        if not prior_responses:
            raise ValueError("Nothing to approve.")
        response_message = prior_responses[-1]
    example = ChatThread([initial_prompt, response_message])

    examples.save(example, env)
    env[ContextEnv].add(ChatMessage(ChatIntent.STATUS, "✅ Example saved."))

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
