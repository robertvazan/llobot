from pathlib import Path
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.stream import record_stream
from llobot.chats.thread import ChatThread
from tests.models.mock import MockModel
from llobot.roles.imitator import Imitator

def get_response_content(thread: ChatThread) -> str:
    """Helper to extract model response content from the thread."""
    for msg in thread:
        if msg.intent == ChatIntent.RESPONSE:
            return msg.content
    return ""

def test_imitator_approve(tmp_path: Path):
    model = MockModel('echo', response="Say B")
    # Imitator saves examples to example_history.
    imitator = Imitator('imitator', model,
                        example_history=tmp_path / "examples",
                        session_history=tmp_path / "sessions")

    # 1. Turn 1: User asks "Say B"
    prompt1 = ChatThread([ChatMessage(ChatIntent.PROMPT, "Say B")])
    thread1 = record_stream(imitator.chat(prompt1))
    response1_content = get_response_content(thread1)

    # 2. Turn 2: User says "@approve".
    # We must pass the full history to ensure context alignment.
    prompt2 = ChatThread([
        ChatMessage(ChatIntent.PROMPT, "Say B"),
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
    record_stream(imitator.chat(prompt_new))
    context_new = model.history[-1]

    # The example should be stuffed into context
    assert "Say B" in context_new

def test_imitator_approve_correction(tmp_path: Path):
    model = MockModel('echo')
    imitator = Imitator('imitator', model,
                        example_history=tmp_path / "examples",
                        session_history=tmp_path / "sessions")

    # Turn 1: "Say C"
    prompt1 = ChatThread([ChatMessage(ChatIntent.PROMPT, "Say C")])
    thread1 = record_stream(imitator.chat(prompt1))
    response1_content = get_response_content(thread1)

    # Turn 2: "@approve C" (providing explicit correction because MockModel output is messy)
    prompt2 = ChatThread([
        ChatMessage(ChatIntent.PROMPT, "Say C"),
        ChatMessage(ChatIntent.RESPONSE, response1_content),
        ChatMessage(ChatIntent.PROMPT, "@approve C")
    ])

    thread2 = record_stream(imitator.chat(prompt2))
    status_msg = next((m for m in thread2 if m.intent == ChatIntent.STATUS), None)
    assert status_msg
    assert "✅ Example saved." in status_msg.content

    # Verify correction
    prompt_new = ChatThread([ChatMessage(ChatIntent.PROMPT, "New task")])
    record_stream(imitator.chat(prompt_new))
    context_new = model.history[-1]

    # The stuffed example should contain the corrected response "C"
    # Example format typically:
    # Example-Prompt: Say C
    # Example-Response: C
    assert "Say C" in context_new
    assert "C" in context_new
