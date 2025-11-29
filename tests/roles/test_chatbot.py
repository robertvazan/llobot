from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.stream import record_stream
from llobot.chats.thread import ChatThread
from llobot.models.echo import EchoModel
from llobot.roles.chatbot import Chatbot

def test_chatbot_chat():
    model = EchoModel('echo')
    role = Chatbot('bot', model, prompt="System Prompt")

    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "Hello")])
    stream = role.chat(prompt)
    response_thread = record_stream(stream)

    assert len(response_thread) == 1
    response = response_thread[0]
    assert response.intent == ChatIntent.RESPONSE
    # EchoModel with default format joins messages with separator
    assert "System Prompt" in response.content
    assert "Okay" in response.content  # Affirmation
    assert "Hello" in response.content
