from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.thread import ChatThread
from llobot.environments.prompt import PromptEnv, _hash_thread

def test_prompt_env_empty():
    env = PromptEnv()
    assert env.full == ChatThread()
    assert env.current == ''
    assert env.hash is None
    assert env.previous_hash is None
    assert not env.swallowed

def test_prompt_env_set():
    env = PromptEnv()
    initial = "Initial prompt"
    prompt = ChatThread([
        ChatMessage(ChatIntent.PROMPT, initial),
        ChatMessage(ChatIntent.RESPONSE, "First response"),
        ChatMessage(ChatIntent.PROMPT, "Current prompt"),
    ])
    env.set(prompt)

    assert env.full == prompt
    assert env.current == "Current prompt"
    assert env.hash is not None
    assert len(env.hash) == 40
    # Hash should be computed from the full thread
    assert env.hash == _hash_thread(prompt)

    # Previous hash should be computed from thread up to "Initial prompt" (inclusive)
    # because "Initial prompt" is the previous message with PROMPT intent.
    previous_thread = ChatThread([
        ChatMessage(ChatIntent.PROMPT, initial),
    ])
    assert env.previous_hash == _hash_thread(previous_thread)

def test_prompt_env_swallow():
    env = PromptEnv()
    assert not env.swallowed
    env.swallow()
    assert env.swallowed

    env.set(ChatThread())
    assert not env.swallowed

def test_prompt_env_set_empty_prompt():
    env = PromptEnv()
    env.set(ChatThread())
    assert env.full == ChatThread()
    assert env.current == ''
    assert env.hash is None
    assert env.previous_hash is None

def test_prompt_env_first_message_empty():
    """Empty message is still part of the thread and should be hashed."""
    env = PromptEnv()
    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "")])
    env.set(prompt)
    assert env.hash is not None
    assert env.hash == _hash_thread(prompt)
