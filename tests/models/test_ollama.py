"""
Tests for Ollama model integration.
"""
from __future__ import annotations
from llobot.models.ollama import OllamaModel
from llobot.models.ollama.endpoints import localhost_ollama_endpoint

def test_value_type():
    """
    Tests that OllamaModel is a value type.
    """
    model1 = OllamaModel(name='local', model='qwen2:7b', num_ctx=8192)
    model2 = OllamaModel(name='local', model='qwen2:7b', num_ctx=8192)
    model3 = OllamaModel(name='remote', model='qwen2:7b', num_ctx=8192)
    assert model1 == model2
    assert model1 != model3
    assert hash(model1) == hash(model2)
    assert model1._endpoint == localhost_ollama_endpoint()
