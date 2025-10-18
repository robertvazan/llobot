from pathlib import Path
from llobot.environments.context import ContextEnv
from llobot.chats.messages import ChatMessage
from llobot.chats.intents import ChatIntent
from llobot.chats.branches import ChatBranch

def test_context_env():
    env = ContextEnv()
    assert not env.populated
    assert not env.build()

    msg1 = ChatMessage(ChatIntent.PROMPT, "Hello")
    env.add(msg1)
    assert env.populated
    assert len(env.build()) == 1
    assert env.build()[0] == msg1

    msg2 = ChatMessage(ChatIntent.RESPONSE, "Hi")
    branch = ChatBranch([msg2])
    env.add(branch)
    assert len(env.build()) == 2
    assert env.build()[1] == msg2

    built = env.build()
    assert isinstance(built, ChatBranch)
    assert len(built) == 2
    assert built[0] == msg1
    assert built[1] == msg2

def test_context_env_persistence(tmp_path: Path):
    env = ContextEnv()
    msg1 = ChatMessage(ChatIntent.PROMPT, "Hello")
    msg2 = ChatMessage(ChatIntent.RESPONSE, "Hi")
    env.add(msg1)
    env.add(msg2)

    save_path = tmp_path / "env"
    env.save(save_path)

    context_md = save_path / 'context.md'
    assert context_md.exists()
    content = context_md.read_text()
    assert '> Prompt' in content
    assert 'Hello' in content
    assert '> Response' in content
    assert 'Hi' in content

    # Test loading
    env2 = ContextEnv()
    env2.load(save_path)
    branch = env2.build()
    assert len(branch) == 2
    assert branch[0] == msg1
    assert branch[1] == msg2

def test_context_env_persistence_empty(tmp_path: Path):
    env = ContextEnv()
    save_path = tmp_path / "env"
    env.save(save_path)

    context_md = save_path / 'context.md'
    assert context_md.exists()
    assert context_md.read_text() == ""

    env2 = ContextEnv()
    env2.load(save_path)
    assert not env2.build()

def test_context_env_load_missing_file(tmp_path: Path):
    env = ContextEnv()
    env.load(tmp_path)
    assert not env.build()
