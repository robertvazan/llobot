"""
Tests for the EchoModel.
"""
from __future__ import annotations
from llobot.chats.branches import ChatBranch
from llobot.chats.messages import ChatMessage
from llobot.chats.intents import ChatIntent
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
    prompt = ChatBranch([
        ChatMessage(ChatIntent.SYSTEM, "System prompt."),
        ChatMessage(ChatIntent.PROMPT, "User prompt.")
    ])
    response_stream = model.generate(prompt)
    response = "".join(response_stream)
    assert response == prompt.monolithic()
