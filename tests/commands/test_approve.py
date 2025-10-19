from pathlib import Path
from llobot.chats.history import standard_chat_history
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.commands.approve import handle_approve_command
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.prompt import PromptEnv
from llobot.environments.status import StatusEnv
from llobot.memories.examples import ExampleMemory

def test_approve_command(tmp_path: Path):
    history = standard_chat_history(tmp_path)
    examples = ExampleMemory('test-role', history=history)
    env = Environment()

    # Setup context
    context = env[ContextEnv]
    context.add(ChatMessage(ChatIntent.PROMPT, "User prompt"))

    # Setup prompt
    prompt_env = env[PromptEnv]
    prompt_env.set("Approved response. @approve")

    # Handle
    assert handle_approve_command('approve', env, examples)

    # Check status
    status = env[StatusEnv]
    assert status.populated
    assert status.content() == "✅ Example saved."

    # Check saved example
    saved_examples = list(examples.recent(env))
    assert len(saved_examples) == 1
    example = saved_examples[0]
    assert len(example.messages) == 2
    assert example[0].intent == ChatIntent.EXAMPLE_PROMPT
    assert example[0].content == "User prompt"
    assert example[1].intent == ChatIntent.EXAMPLE_RESPONSE
    assert example[1].content == "Approved response."

def test_approve_command_full_chat(tmp_path: Path):
    history = standard_chat_history(tmp_path)
    examples = ExampleMemory('test-role', history=history)
    env = Environment()

    # Setup context
    context = env[ContextEnv]
    context.add(ChatMessage(ChatIntent.PROMPT, "User prompt 1"))
    context.add(ChatMessage(ChatIntent.RESPONSE, "Model response 1"))
    context.add(ChatMessage(ChatIntent.PROMPT, "User prompt 2"))

    # Handle (no prompt in PromptEnv)
    assert handle_approve_command('approve', env, examples)

    # Check status
    assert env[StatusEnv].populated

    # Check saved example
    saved_examples = list(examples.recent(env))
    assert len(saved_examples) == 1
    example = saved_examples[0]
    assert len(example.messages) == 3
    assert example[0].intent == ChatIntent.EXAMPLE_PROMPT
    assert example[0].content == "User prompt 1"
    assert example[1].intent == ChatIntent.EXAMPLE_RESPONSE
    assert example[1].content == "Model response 1"
    assert example[2].intent == ChatIntent.EXAMPLE_PROMPT
    assert example[2].content == "User prompt 2"

def test_approve_command_empty_stripped_prompt(tmp_path: Path):
    history = standard_chat_history(tmp_path)
    examples = ExampleMemory('test-role', history=history)
    env = Environment()

    # Setup context
    context = env[ContextEnv]
    context.add(ChatMessage(ChatIntent.PROMPT, "User prompt 1"))
    context.add(ChatMessage(ChatIntent.RESPONSE, "Model response 1"))

    # Setup prompt that is empty after stripping
    prompt_env = env[PromptEnv]
    prompt_env.set("@approve")

    # Handle
    assert handle_approve_command('approve', env, examples)

    # Check status
    assert env[StatusEnv].populated

    # Check that the whole context was saved
    saved_examples = list(examples.recent(env))
    assert len(saved_examples) == 1
    example = saved_examples[0]
    assert len(example.messages) == 2
    assert example[0].content == "User prompt 1"
    assert example[1].content == "Model response 1"
