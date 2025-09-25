"""
Tests for OpenAI model integration.
"""
from __future__ import annotations
from llobot.models.openai import OpenAIModel

def test_value_type():
    """
    Tests that OpenAIModel is a value type.
    """
    model1 = OpenAIModel(name='gpt4', model='gpt-4o', auth='key1')
    model2 = OpenAIModel(name='gpt4', model='gpt-4o', auth='key1')
    model3 = OpenAIModel(name='gpt3', model='gpt-3.5-turbo', auth='key1')
    assert model1 == model2
    assert model1 != model3
    assert hash(model1) == hash(model2)
    assert 'key1' not in repr(model1)
