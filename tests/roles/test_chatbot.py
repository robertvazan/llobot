from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.stream import record_stream
from llobot.chats.thread import ChatThread
from tests.models.mock import MockModel
from llobot.roles.chatbot import Chatbot

def test_chatbot_chat():
    model = MockModel('echo', response="canned")
    role = Chatbot('bot', model, prompt="System Prompt")

    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "Hello")])
    stream = role.chat(prompt)
    response_thread = record_stream(stream)

    assert len(response_thread) == 1
    response = response_thread[0]
    assert response.intent == ChatIntent.RESPONSE
    assert response.content == "canned"

    context = model.history[0]
    assert "System Prompt" in context
    assert "Hello" in context
