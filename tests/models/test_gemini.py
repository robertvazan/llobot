"""
Tests for Gemini model integration.
"""
from __future__ import annotations
from unittest.mock import MagicMock
from google.genai import types
from llobot.chats.builder import ChatBuilder
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.models.gemini import GeminiModel
import pytest

def test_value_type_gemini():
    """
    Tests that GeminiModel is a value type.
    """
    model1 = GeminiModel(name='gemini', model='gemini-1.5-flash', auth='key1')
    model2 = GeminiModel(name='gemini', model='gemini-1.5-flash', auth='key1')
    model3 = GeminiModel(name='gemini-pro', model='gemini-1.5-pro', auth='key1')
    assert model1 == model2
    assert model1 != model3
    assert hash(model1) == hash(model2)
    assert 'key1' not in repr(model1)

def test_default_name():
    model = GeminiModel(model='gemini-1.5-flash', auth='key1')
    assert model.name == 'gemini-1.5-flash'

def test_identifier():
    model = GeminiModel(name='gemini', model='gemini-1.5-flash', auth='key')
    assert model.identifier == 'google/gemini-1.5-flash'

def test_missing_model():
    """
    Tests that `model` parameter is mandatory.
    """
    with pytest.raises(TypeError):
        GeminiModel(name='gemini', auth='key') # type: ignore[reportCallIssue]

def test_thinking_removed():
    """
    Tests that `thinking` parameter is no longer accepted.
    """
    with pytest.raises(TypeError):
        GeminiModel(model='gemini-1.5-flash', auth='key', thinking=1000) # type: ignore[reportCallIssue]

def test_thinking_level():
    """
    Tests that thinking_level parameter is accepted and preserved.
    """
    model1 = GeminiModel(model='gemini-3-pro', auth='key', thinking_level='HIGH')
    model2 = GeminiModel(model='gemini-3-pro', auth='key', thinking_level='HIGH')
    model3 = GeminiModel(model='gemini-3-pro', auth='key', thinking_level=None)
    assert model1 == model2
    assert model1 != model3
    assert hash(model1) == hash(model2)

def test_thinking_level_types():
    """
    Tests that thinking_level enum and string are treated equally.
    """
    model_str = GeminiModel(model='gemini-3-pro', auth='key', thinking_level='HIGH')
    model_enum = GeminiModel(model='gemini-3-pro', auth='key', thinking_level=types.ThinkingLevel.HIGH)
    assert model_str == model_enum

def test_thinking_level_emission():
    """
    Tests that thinking_config is correctly emitted in generate_content_stream call.
    """
    mock_client = MagicMock()
    mock_client.models.generate_content_stream.return_value = []

    model = GeminiModel(model='gemini-3-pro', client=mock_client, thinking_level='HIGH')
    msg = ChatMessage(intent=ChatIntent.PROMPT, content="Hello")
    builder = ChatBuilder()
    builder.add(msg)
    prompt = builder.build()
    list(model.generate(prompt))

    mock_client.models.generate_content_stream.assert_called_once()
    kwargs = mock_client.models.generate_content_stream.call_args.kwargs
    assert 'config' in kwargs
    assert kwargs['config'].thinking_config.thinking_level == types.ThinkingLevel.HIGH

    mock_client.reset_mock()
    model_none = GeminiModel(model='gemini-3-pro', client=mock_client)
    list(model_none.generate(prompt))

    kwargs_none = mock_client.models.generate_content_stream.call_args.kwargs
    assert kwargs_none['config'].thinking_config is None
