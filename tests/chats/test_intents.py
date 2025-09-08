import pytest
from llobot.chats.intents import ChatIntent

def test_str():
    """Tests that str(intent) returns its value."""
    assert str(ChatIntent.SYSTEM) == 'System'
    assert str(ChatIntent.PROMPT) == 'Prompt'
    assert str(ChatIntent.RESPONSE) == 'Response'

def test_parse():
    """Tests parsing intent from string."""
    assert ChatIntent.parse('System') == ChatIntent.SYSTEM
    assert ChatIntent.parse('Prompt') == ChatIntent.PROMPT
    assert ChatIntent.parse('Response') == ChatIntent.RESPONSE
    with pytest.raises(ValueError):
        ChatIntent.parse('InvalidIntent')

def test_parse_roundtrip():
    """Tests that parse(str(intent)) is identity."""
    for intent in ChatIntent:
        assert ChatIntent.parse(str(intent)) == intent
