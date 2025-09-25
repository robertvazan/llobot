"""
Tests for OpenAI model integration.
"""
from __future__ import annotations
import pytest
from llobot.models.openai import OpenAIModel

def test_value_type():
    """
    Tests that OpenAIModel is a value type.
    """
    model1 = OpenAIModel(name='gpt4', auth='key1', model='gpt-4o')
    model2 = OpenAIModel(name='gpt4', auth='key1', model='gpt-4o')
    model3 = OpenAIModel(name='gpt3', auth='key1', model='gpt-3.5-turbo')
    assert model1 == model2
    assert model1 != model3
    assert hash(model1) == hash(model2)
    assert 'key1' not in repr(model1)

def test_missing_auth():
    """
    Tests that `auth` parameter is mandatory.
    """
    with pytest.raises(TypeError):
        OpenAIModel(name='gpt4')
