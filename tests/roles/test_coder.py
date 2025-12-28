from pathlib import Path
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.stream import record_stream
from llobot.chats.thread import ChatThread
from llobot.models.echo import EchoModel
from llobot.roles.coder import Coder

def get_response_content(thread: ChatThread) -> str:
    """Helper to extract model response content from the thread."""
    for msg in thread:
        if msg.intent == ChatIntent.RESPONSE:
            return msg.content
    return ""

def test_coder_instantiation(tmp_path: Path):
    model = EchoModel('echo')
    coder = Coder('coder', model, session_history=tmp_path)

    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "Code something")])
    response = get_response_content(record_stream(coder.chat(prompt)))

    # Check that coder-specific system prompts are present
    assert "When asked to edit code" in response
    assert "Tools" in response
    assert "Code blocks" in response
    assert "File listings" in response
