from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.stream import record_stream
from llobot.chats.thread import ChatThread
from tests.models.mock import MockModel
from llobot.roles.chatbot import Chatbot
from llobot.roles.models import RoleModel

def test_role_model_wrapper():
    # Setup
    base_model = MockModel('echo', response="Mock Response")
    role = Chatbot('bot', base_model, prompt="SYS")
    role_model = RoleModel(role)

    assert role_model.name == 'bot'
    assert role_model.identifier == 'llobot/bot'

    # Generate
    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "Hi")])
    stream = role_model.generate(prompt)
    response = record_stream(stream)

    assert len(response) == 1
    content = response[0].content

    assert content == "Mock Response"

    # Verify that the role properly constructed the context passed to the model
    context = base_model.history[0]
    assert "SYS" in context
    assert "Hi" in context

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
