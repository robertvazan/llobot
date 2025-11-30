from pathlib import Path
from llobot.environments.context import ContextEnv
from llobot.chats.message import ChatMessage
from llobot.chats.intent import ChatIntent
from llobot.chats.thread import ChatThread

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
    chat = ChatThread([msg2])
    env.add(chat)
    assert len(env.build()) == 2
    assert env.build()[1] == msg2

    built = env.build()
    assert isinstance(built, ChatThread)
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
    chat = env2.build()
    assert len(chat) == 2
    assert chat[0] == msg1
    assert chat[1] == msg2

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

def test_coerce_no_change():
    """Context is a superset of visible, with no conversational messages after."""
    env = ContextEnv()
    env.add(ChatThread([
        ChatMessage(ChatIntent.PROMPT, "p1"),
        ChatMessage(ChatIntent.RESPONSE, "r1"),
        ChatMessage(ChatIntent.SYSTEM, "sys"),
    ]))
    visible = ChatThread([
        ChatMessage(ChatIntent.PROMPT, "p1"),
        ChatMessage(ChatIntent.RESPONSE, "r1"),
    ])
    env.coerce(visible)
    assert env.build().messages == (
        ChatMessage(ChatIntent.PROMPT, "p1"),
        ChatMessage(ChatIntent.RESPONSE, "r1"),
        ChatMessage(ChatIntent.SYSTEM, "sys"),
    )

def test_coerce_truncate_conversational():
    """Context is a superset of visible, with conversational messages after."""
    env = ContextEnv()
    env.add(ChatThread([
        ChatMessage(ChatIntent.PROMPT, "p1"),
        ChatMessage(ChatIntent.RESPONSE, "r1"),
        ChatMessage(ChatIntent.SYSTEM, "sys"), # non-conversational
        ChatMessage(ChatIntent.PROMPT, "p2"),  # conversational
        ChatMessage(ChatIntent.RESPONSE, "r2"),
    ]))
    visible = ChatThread([
        ChatMessage(ChatIntent.PROMPT, "p1"),
        ChatMessage(ChatIntent.RESPONSE, "r1"),
    ])
    env.coerce(visible)
    # Everything after r1 is truncated because p2 is conversational.
    # sys is removed because it is in the truncated tail (after r1).
    assert env.build().messages == (
        ChatMessage(ChatIntent.PROMPT, "p1"),
        ChatMessage(ChatIntent.RESPONSE, "r1"),
    )

def test_coerce_append():
    """Context is a subset of visible."""
    env = ContextEnv()
    env.add(ChatThread([
        ChatMessage(ChatIntent.PROMPT, "p1"),
        ChatMessage(ChatIntent.RESPONSE, "r1"),
    ]))
    visible = ChatThread([
        ChatMessage(ChatIntent.PROMPT, "p1"),
        ChatMessage(ChatIntent.RESPONSE, "r1"),
        ChatMessage(ChatIntent.PROMPT, "p2"),
    ])
    env.coerce(visible)
    assert env.build().messages == visible.messages

def test_coerce_mismatch():
    """Context and visible history mismatch in content."""
    env = ContextEnv()
    env.add(ChatThread([
        ChatMessage(ChatIntent.PROMPT, "p1"),
        ChatMessage(ChatIntent.RESPONSE, "r1-wrong"),
        ChatMessage(ChatIntent.PROMPT, "p2"),
    ]))
    visible = ChatThread([
        ChatMessage(ChatIntent.PROMPT, "p1"),
        ChatMessage(ChatIntent.RESPONSE, "r1-correct"),
        ChatMessage(ChatIntent.PROMPT, "p2-new"),
    ])
    env.coerce(visible)
    # Context is truncated at mismatch point (r1), and rest of visible is appended.
    assert env.build().messages == (
        ChatMessage(ChatIntent.PROMPT, "p1"),
        ChatMessage(ChatIntent.RESPONSE, "r1-correct"),
        ChatMessage(ChatIntent.PROMPT, "p2-new"),
    )

def test_coerce_empty_context():
    """Context is empty, visible has messages."""
    env = ContextEnv()
    visible = ChatThread([
        ChatMessage(ChatIntent.PROMPT, "p1"),
        ChatMessage(ChatIntent.RESPONSE, "r1"),
    ])
    env.coerce(visible)
    assert env.build().messages == visible.messages

def test_coerce_empty_visible():
    """Visible history is empty, context has messages."""
    env = ContextEnv()
    env.add(ChatThread([
        ChatMessage(ChatIntent.SYSTEM, "sys"),
        ChatMessage(ChatIntent.PROMPT, "p1"),
        ChatMessage(ChatIntent.RESPONSE, "r1"),
    ]))
    visible = ChatThread()
    env.coerce(visible)
    # p1 is conversational, so context is truncated before it.
    # Since p1 (and sys) are in the tail (after -1), they are removed.
    assert env.build().messages == ()

def test_coerce_both_empty():
    """Both context and visible history are empty."""
    env = ContextEnv()
    visible = ChatThread()
    env.coerce(visible)
    assert not env.build()

def test_coerce_complex_pairing():
    """Tests coercion with non-conversational messages interspersed."""
    env = ContextEnv()
    env.add(ChatThread([
        ChatMessage(ChatIntent.SYSTEM, "sys1"),
        ChatMessage(ChatIntent.PROMPT, "p1"),
        ChatMessage(ChatIntent.SYSTEM, "sys2"),
        ChatMessage(ChatIntent.RESPONSE, "r1"),
        ChatMessage(ChatIntent.PROMPT, "p2"), # This will be a mismatch
    ]))
    visible = ChatThread([
        ChatMessage(ChatIntent.PROMPT, "p1"),
        ChatMessage(ChatIntent.RESPONSE, "r1"),
        ChatMessage(ChatIntent.PROMPT, "p2-edited"),
    ])
    env.coerce(visible)
    # Pairing:
    # visible p1 (idx 0) -> context p1 (idx 1). Skipped sys1 (OK, non-conversational).
    # visible r1 (idx 1) -> context r1 (idx 3). Skipped sys2 (OK).
    # visible p2-edited (idx 2) != context p2 (idx 4) -> mismatch.
    # Truncate context at index 4, and append visible from index 2.
    # Preserves sys1 and sys2 because they were skipped during successful matches.
    assert env.build().messages == (
        ChatMessage(ChatIntent.SYSTEM, "sys1"),
        ChatMessage(ChatIntent.PROMPT, "p1"),
        ChatMessage(ChatIntent.SYSTEM, "sys2"),
        ChatMessage(ChatIntent.RESPONSE, "r1"),
        ChatMessage(ChatIntent.PROMPT, "p2-edited"),
    )

def test_coerce_truncate_just_after_last_pair():
    """Test truncation when conversational message is right after last paired message."""
    env = ContextEnv()
    env.add(ChatThread([
        ChatMessage(ChatIntent.PROMPT, "p1"),
        ChatMessage(ChatIntent.RESPONSE, "r1"),
        ChatMessage(ChatIntent.PROMPT, "p2"), # conversational
        ChatMessage(ChatIntent.SYSTEM, "sys"), # non-conversational after
    ]))
    visible = ChatThread([
        ChatMessage(ChatIntent.PROMPT, "p1"),
        ChatMessage(ChatIntent.RESPONSE, "r1"),
    ])
    env.coerce(visible)
    assert env.build().messages == (
        ChatMessage(ChatIntent.PROMPT, "p1"),
        ChatMessage(ChatIntent.RESPONSE, "r1"),
    )

def test_coerce_mismatch_in_intent_pairing():
    """Test where visible has an extra message that cannot be paired."""
    env = ContextEnv()
    env.add(ChatThread([
        ChatMessage(ChatIntent.PROMPT, "p1"),
        ChatMessage(ChatIntent.RESPONSE, "r1"),
    ]))
    visible = ChatThread([
        ChatMessage(ChatIntent.PROMPT, "p1"),
        ChatMessage(ChatIntent.PROMPT, "p1.5"), # Cannot be paired
        ChatMessage(ChatIntent.RESPONSE, "r1"),
    ])
    env.coerce(visible)
    # Pairing: visible p1 -> context p1.
    # visible p1.5 (conversational) does not match context r1.
    # Loop match fails.
    # Pairs: [(0, 0)]. Last paired: p1.
    # Tail in context: r1.
    # r1 is conversational.
    # Truncate after p1.
    # Append p1.5, r1.
    # Result: p1, p1.5, r1.
    assert env.build().messages == visible.messages

def test_coerce_skipped_conversational_aborts():
    """Test that we do not skip conversational messages in context."""
    env = ContextEnv()
    env.add(ChatThread([
        ChatMessage(ChatIntent.PROMPT, "p1"),
        ChatMessage(ChatIntent.PROMPT, "p2"), # Context has p2
    ]))
    visible = ChatThread([
        ChatMessage(ChatIntent.PROMPT, "p1"),
        ChatMessage(ChatIntent.PROMPT, "p3"), # Visible skips p2 to try matching p3? No.
    ])
    # Match p1 -> p1.
    # Match p3 -> search context. p2 is skipped. p2 is conversational.
    # Abort match.
    # Pairs: [(0, 0)].
    # Tail: p2. Conversational.
    # Truncate after p1.
    # Append p3.
    # Result: p1, p3.
    env.coerce(visible)
    assert env.build().messages == visible.messages
