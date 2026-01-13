from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.stream import record_stream
from llobot.chats.thread import ChatThread
from tests.mock_model import MockModel
from llobot.roles.chatbot import Chatbot
from llobot.roles.models import RoleModel

def test_role_model_wrapper():
    # Setup
    base_model = MockModel('echo')
    role = Chatbot('bot', base_model, prompt="SYS")
    role_model = RoleModel(role)

    assert role_model.name == 'bot'

    # Generate
    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "Hi")])
    stream = role_model.generate(prompt)
    response = record_stream(stream)

    assert len(response) == 1
    content = response[0].content

    # Verify content
    # The RoleModel wraps the output of Chatbot (which wraps output of MockModel)
    # Chatbot sends [System(SYS), Prompt(Hi)] to MockModel.
    # MockModel returns "SYS\n\n---\n\nHi".
    # RoleModel should yield this content (via submessage format if needed, but plain string here).
    assert "SYS" in content
    assert "Hi" in content

def test_role_model_exception_handling():
    # Create a broken role
    class BrokenRole:
        @property
        def name(self): return "broken"
        def chat(self, prompt):
            raise ValueError("Something went wrong")

    role_model = RoleModel(BrokenRole())

    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "Hi")])
    stream = role_model.generate(prompt)
    response = record_stream(stream)

    # Should yield a STATUS message with error details
    assert len(response) == 1
    msg = response[0]
    assert msg.intent == ChatIntent.STATUS
    assert "❌ `Something went wrong`" in msg.content
    assert "Stack trace" in msg.content
