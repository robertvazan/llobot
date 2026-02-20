from pathlib import Path
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.stream import record_stream
from llobot.chats.thread import ChatThread
from tests.models.mock import MockModel
from llobot.roles.coder import Coder

def test_coder_instantiation(tmp_path: Path):
    model = MockModel(name='echo')
    coder = Coder('coder', model, session_history=tmp_path)

    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "Code something")])
    record_stream(coder.chat(prompt))
    context = model.history[0]
    assert "Software developer's guidelines" in context
    assert "How to ask questions" in context
    assert "How to write closing remarks" in context
