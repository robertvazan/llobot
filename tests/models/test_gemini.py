"""
Tests for Gemini model integration.
"""
from __future__ import annotations
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
