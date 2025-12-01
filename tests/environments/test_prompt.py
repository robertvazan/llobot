import base64
import hashlib
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.thread import ChatThread
from llobot.environments.prompt import PromptEnv

def _session_hash(text: str) -> str:
    hasher = hashlib.sha256(text.encode('utf-8'))
    b64 = base64.urlsafe_b64encode(hasher.digest()).decode('ascii')
    return b64[:40]

def test_prompt_env_empty():
    env = PromptEnv()
    assert env.full == ChatThread()
    assert env.current == ''
    assert env.hash is None

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
    assert env.hash == _session_hash(initial)

def test_prompt_env_set_empty_prompt():
    env = PromptEnv()
    env.set(ChatThread())
    assert env.full == ChatThread()
    assert env.current == ''
    assert env.hash is None

def test_prompt_env_first_message_empty():
    env = PromptEnv()
    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "")])
    env.set(prompt)
    assert env.hash is None
