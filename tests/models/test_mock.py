"""
Tests for MockModel.
"""
from __future__ import annotations
from tests.models.mock import MockModel

def test_identifier():
    model = MockModel(name='mock1')
    assert model.identifier == 'mock/mock1'
