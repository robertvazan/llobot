from pathlib import Path
from llobot.chats.history import standard_chat_history
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.thread import ChatThread
from llobot.commands.approve import handle_approve_command
from llobot.environments import Environment
from llobot.environments.prompt import PromptEnv
from llobot.environments.status import StatusEnv
from llobot.memories.examples import ExampleMemory

def test_approve_command(tmp_path: Path):
    history = standard_chat_history(tmp_path)
    examples = ExampleMemory('test-role', history=history)
    env = Environment()

    # Setup prompt
    prompt_env = env[PromptEnv]
    prompt_env.set(ChatThread([
        ChatMessage(ChatIntent.PROMPT, "User prompt"),
        ChatMessage(ChatIntent.PROMPT, "Approved response. @approve"),
    ]))

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

    # Setup prompt with intermediate conversation
    prompt_env = env[PromptEnv]
    prompt_env.set(ChatThread([
        ChatMessage(ChatIntent.PROMPT, "User prompt 1"),
        ChatMessage(ChatIntent.RESPONSE, "Model response 1"),
        ChatMessage(ChatIntent.PROMPT, "Refinement prompt"),
        ChatMessage(ChatIntent.RESPONSE, "Final model response"),
        ChatMessage(ChatIntent.PROMPT, "@approve"),
    ]))

    # Handle
    assert handle_approve_command('approve', env, examples)

    # Check status
    assert env[StatusEnv].populated

    # Check that only initial prompt and final response are saved
    saved_examples = list(examples.recent(env))
    assert len(saved_examples) == 1
    example = saved_examples[0]
    assert len(example.messages) == 2
    assert example[0].intent == ChatIntent.EXAMPLE_PROMPT
    assert example[0].content == "User prompt 1"
    assert example[1].intent == ChatIntent.EXAMPLE_RESPONSE
    assert example[1].content == "Final model response"

def test_approve_command_empty_stripped_prompt(tmp_path: Path):
    history = standard_chat_history(tmp_path)
    examples = ExampleMemory('test-role', history=history)
    env = Environment()

    # Setup prompt that is empty after stripping
    prompt_env = env[PromptEnv]
    prompt_env.set(ChatThread([
        ChatMessage(ChatIntent.PROMPT, "User prompt 1"),
        ChatMessage(ChatIntent.RESPONSE, "Model response 1"),
        ChatMessage(ChatIntent.PROMPT, "@approve"),
    ]))

    # Handle
    assert handle_approve_command('approve', env, examples)

    # Check status
    assert env[StatusEnv].populated

    # Check that the initial prompt and last response were saved
    saved_examples = list(examples.recent(env))
    assert len(saved_examples) == 1
    example = saved_examples[0]
    assert len(example.messages) == 2
    assert example[0].content == "User prompt 1"
    assert example[1].content == "Model response 1"
