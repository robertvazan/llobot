"""
Tests for Gemini model integration.
"""
from __future__ import annotations
from llobot.models.gemini import GeminiModel

def test_value_type():
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
