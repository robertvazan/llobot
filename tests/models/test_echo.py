"""
Tests for the EchoModel.
"""
from __future__ import annotations
from llobot.chats.thread import ChatThread
from llobot.chats.message import ChatMessage
from llobot.chats.intent import ChatIntent
from llobot.chats.monolithic import monolithic_chat
from llobot.models.echo import EchoModel

def test_value_type():
    """
    Tests that EchoModel is a value type.
    """
    model1 = EchoModel('echo1', context_budget=100)
    model2 = EchoModel('echo1', context_budget=100)
    model3 = EchoModel('echo2', context_budget=100)
    assert model1 == model2
    assert model1 != model3
    assert hash(model1) == hash(model2)

def test_generate():
    """
    Tests that EchoModel correctly echoes the prompt.
    """
    model = EchoModel('echo')
    prompt = ChatThread([
        ChatMessage(ChatIntent.SYSTEM, "System prompt."),
        ChatMessage(ChatIntent.PROMPT, "User prompt.")
    ])
    response_stream = model.generate(prompt)
    response = "".join(response_stream)
    assert response == monolithic_chat(prompt)
