"""
Tests for the EchoModel.
"""
from __future__ import annotations
from llobot.chats.thread import ChatThread
from llobot.chats.message import ChatMessage
from llobot.chats.intent import ChatIntent
from llobot.models.echo import EchoModel
from llobot.formats.monolithic.details import DetailsMonolithicFormat

def test_value_type():
    """
    Tests that EchoModel is a value type.
    """
    model1 = EchoModel('echo1', context_budget=100)
    model2 = EchoModel('echo1', context_budget=100)
    model3 = EchoModel('echo2', context_budget=100)
    model4 = EchoModel('echo1', context_budget=100, format=DetailsMonolithicFormat())
    assert model1 == model2
    assert model1 != model3
    assert model1 != model4
    assert hash(model1) == hash(model2)

def test_generate():
    """
    Tests that EchoModel correctly echoes the prompt using the default format.
    """
    model = EchoModel('echo')
    prompt = ChatThread([
        ChatMessage(ChatIntent.SYSTEM, "System prompt."),
        ChatMessage(ChatIntent.PROMPT, "User prompt.")
    ])
    response_stream = model.generate(prompt)
    response = "".join(s for s in response_stream if isinstance(s, str))
    assert response == "System prompt.\n\n---\n\nUser prompt."

def test_generate_with_custom_format():
    """
    Tests that EchoModel correctly echoes the prompt using a custom format.
    """
    model = EchoModel('echo', format=DetailsMonolithicFormat())
    prompt = ChatThread([
        ChatMessage(ChatIntent.SYSTEM, "System prompt."),
        ChatMessage(ChatIntent.PROMPT, "User prompt.")
    ])
    response_stream = model.generate(prompt)
    response = "".join(s for s in response_stream if isinstance(s, str))
    expected = "<details>\n<summary>System</summary>\n\nSystem prompt.\n\n</details>\n\n<details>\n<summary>Prompt</summary>\n\nUser prompt.\n\n</details>"
    assert response == expected
