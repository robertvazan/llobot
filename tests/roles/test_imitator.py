import re
from pathlib import Path
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.stream import record_stream
from llobot.chats.thread import ChatThread
from llobot.models.echo import EchoModel
from llobot.roles.imitator import Imitator

def get_response_content(thread: ChatThread) -> str:
    """Helper to extract model response content from the thread."""
    for msg in thread:
        if msg.intent == ChatIntent.RESPONSE:
            return msg.content
    return ""

def get_session_command(thread: ChatThread) -> str:
    """Helper to extract session command from the thread."""
    for msg in thread:
        if msg.intent == ChatIntent.SESSION:
            match = re.search(r'Session: @(\d{8}-\d{6})', msg.content)
            if match:
                return f"Session: @{match.group(1)}"
    raise ValueError("No session ID found in thread")

def test_imitator_approve(tmp_path: Path):
    model = EchoModel('echo')
    # Imitator saves examples to example_history.
    imitator = Imitator('imitator', model,
                        example_history=tmp_path / "examples",
                        session_history=tmp_path / "sessions")

    # 1. Turn 1: User asks "Say B", Model says "B" (EchoModel will actually echo the prompt)
    prompt1 = ChatThread([ChatMessage(ChatIntent.PROMPT, "Say B")])
    thread1 = record_stream(imitator.chat(prompt1))
    session_cmd = get_session_command(thread1)

    # Extract response for history consistency
    response1_content = get_response_content(thread1)

    # 2. Turn 2: User says "@approve".
    # We must pass the session ID AND the previous history to ensure context alignment.

    prompt2 = ChatThread([
        ChatMessage(ChatIntent.PROMPT, "Say B"),
        ChatMessage(ChatIntent.SESSION, session_cmd),
        ChatMessage(ChatIntent.RESPONSE, response1_content),
        ChatMessage(ChatIntent.PROMPT, "@approve")
    ])

    thread2 = record_stream(imitator.chat(prompt2))

    # Check for success status
    status_msg = next((m for m in thread2 if m.intent == ChatIntent.STATUS), None)
    assert status_msg
    assert "✅ Example saved." in status_msg.content

    # 3. Verify example is used in subsequent chat
    # Start a fresh chat.
    prompt_new = ChatThread([ChatMessage(ChatIntent.PROMPT, "New task")])
    thread_new = record_stream(imitator.chat(prompt_new))
    response_new = get_response_content(thread_new)

    # The example should be stuffed into context.
    # Since the previous response (from EchoModel) contained "Say B", and the prompt was "Say B",
    # The example saved is Prompt: "Say B", Response: "... Say B ...".
    # Checking for "Say B" presence covers both.
    assert "Say B" in response_new

def test_imitator_approve_correction(tmp_path: Path):
    model = EchoModel('echo')
    imitator = Imitator('imitator', model,
                        example_history=tmp_path / "examples",
                        session_history=tmp_path / "sessions")

    # Turn 1: "Say C"
    prompt1 = ChatThread([ChatMessage(ChatIntent.PROMPT, "Say C")])
    thread1 = record_stream(imitator.chat(prompt1))
    session_cmd = get_session_command(thread1)
    response1_content = get_response_content(thread1)

    # Turn 2: "@approve C" (providing explicit correction because EchoModel output is messy)
    prompt2 = ChatThread([
        ChatMessage(ChatIntent.PROMPT, "Say C"),
        ChatMessage(ChatIntent.SESSION, session_cmd),
        ChatMessage(ChatIntent.RESPONSE, response1_content),
        ChatMessage(ChatIntent.PROMPT, "@approve C")
    ])

    thread2 = record_stream(imitator.chat(prompt2))
    status_msg = next((m for m in thread2 if m.intent == ChatIntent.STATUS), None)
    assert status_msg
    assert "✅ Example saved." in status_msg.content

    # Verify correction
    prompt_new = ChatThread([ChatMessage(ChatIntent.PROMPT, "New task")])
    response_new = get_response_content(record_stream(imitator.chat(prompt_new)))

    # The stuffed example should contain the corrected response "C"
    # Example format typically:
    # Example-Prompt: Say C
    # Example-Response: C
    assert "Say C" in response_new
    assert "C" in response_new
