"""
Tests for Anthropic model integration.
"""
from __future__ import annotations
from llobot.models.anthropic import AnthropicModel
import pytest

def test_value_type_anthropic():
    """
    Tests that AnthropicModel is a value type.
    """
    model1 = AnthropicModel(name='claude', model='claude-3-opus-20240229', auth='key1')
    model2 = AnthropicModel(name='claude', model='claude-3-opus-20240229', auth='key1')
    model3 = AnthropicModel(name='claude-sonnet', model='claude-3-sonnet-20240229', auth='key1')
    assert model1 == model2
    assert model1 != model3
    assert hash(model1) == hash(model2)
    assert hash(model1) != hash(model3)
    assert 'key1' not in repr(model1) # auth key should not be in repr

def test_default_name():
    model = AnthropicModel(model='claude-3-opus-20240229', auth='key1')
    assert model.name == 'claude-3-opus-20240229'

def test_identifier():
    model = AnthropicModel(name='claude', model='claude-3-opus-20240229', auth='key')
    assert model.identifier == 'anthropic/claude-3-opus-20240229'

def test_missing_model():
    """
    Tests that `model` parameter is mandatory.
    """
    with pytest.raises(TypeError):
        AnthropicModel(name='claude', auth='key') # type: ignore[reportCallIssue]
