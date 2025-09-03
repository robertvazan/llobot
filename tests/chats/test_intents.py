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

def test_as_example():
    """Tests conversion to example intents."""
    assert ChatIntent.SYSTEM.as_example() == ChatIntent.EXAMPLE_PROMPT
    assert ChatIntent.SESSION.as_example() == ChatIntent.EXAMPLE_PROMPT
    assert ChatIntent.PROMPT.as_example() == ChatIntent.EXAMPLE_PROMPT
    assert ChatIntent.EXAMPLE_PROMPT.as_example() == ChatIntent.EXAMPLE_PROMPT

    assert ChatIntent.AFFIRMATION.as_example() == ChatIntent.EXAMPLE_RESPONSE
    assert ChatIntent.RESPONSE.as_example() == ChatIntent.EXAMPLE_RESPONSE
    assert ChatIntent.EXAMPLE_RESPONSE.as_example() == ChatIntent.EXAMPLE_RESPONSE
