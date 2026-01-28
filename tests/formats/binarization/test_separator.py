from llobot.chats.thread import ChatThread
from llobot.chats.message import ChatMessage
from llobot.chats.intent import ChatIntent
from llobot.formats.binarization.separator import SeparatorBinarizationFormat

def test_binarize_intent():
    """Tests that intents are correctly mapped to PROMPT or RESPONSE."""
    fmt = SeparatorBinarizationFormat()
    assert fmt.binarize_intent(ChatIntent.SYSTEM) == ChatIntent.PROMPT
    assert fmt.binarize_intent(ChatIntent.EXAMPLE_PROMPT) == ChatIntent.PROMPT
    assert fmt.binarize_intent(ChatIntent.PROMPT) == ChatIntent.PROMPT
    assert fmt.binarize_intent(ChatIntent.STATUS) == ChatIntent.PROMPT

    assert fmt.binarize_intent(ChatIntent.EXAMPLE_RESPONSE) == ChatIntent.RESPONSE
    assert fmt.binarize_intent(ChatIntent.RESPONSE) == ChatIntent.RESPONSE

def test_binarize_chat_merging():
    """Tests that consecutive messages of same binarized intent are merged."""
    fmt = SeparatorBinarizationFormat(separator='|')
    chat = ChatThread([
        ChatMessage(ChatIntent.SYSTEM, "sys"),
        ChatMessage(ChatIntent.PROMPT, "p1"),
        ChatMessage(ChatIntent.STATUS, "stat"),
        ChatMessage(ChatIntent.RESPONSE, "r1"),
    ])

    binarized = fmt.binarize_chat(chat)
    assert len(binarized) == 2

    # SYSTEM, PROMPT, STATUS -> PROMPT group
    assert binarized[0].intent == ChatIntent.PROMPT
    # Mixed original intents use the separator, except SYSTEM/STATUS
    assert binarized[0].content == "sys|p1|stat"

    # RESPONSE -> RESPONSE group
    assert binarized[1].intent == ChatIntent.RESPONSE
    assert binarized[1].content == "r1"

def test_binarize_chat_smart_merging():
    """Tests smart merging of same original intents and system/status."""
    fmt = SeparatorBinarizationFormat(separator='|')
    chat = ChatThread([
        ChatMessage(ChatIntent.PROMPT, "p1"),
        ChatMessage(ChatIntent.PROMPT, "p2"),
        ChatMessage(ChatIntent.SYSTEM, "sys"),
        ChatMessage(ChatIntent.STATUS, "stat"),
        ChatMessage(ChatIntent.PROMPT, "p3"),
    ])

    binarized = fmt.binarize_chat(chat)
    assert len(binarized) == 1

    # p1 + \n\n + p2 (same original intent)
    # + | + sys (different intent)
    # + \n\n + stat (sys/stat rule)
    # + | + p3 (different intent)
    assert binarized[0].content == "p1\n\np2|sys\n\nstat|p3"

def test_binarize_chat_alternating():
    """Tests that alternating messages are preserved."""
    fmt = SeparatorBinarizationFormat()
    chat = ChatThread([
        ChatMessage(ChatIntent.PROMPT, "p1"),
        ChatMessage(ChatIntent.RESPONSE, "r1"),
        ChatMessage(ChatIntent.PROMPT, "p2"),
    ])

    binarized = fmt.binarize_chat(chat)
    assert len(binarized) == 3
    assert binarized[0].content == "p1"
    assert binarized[1].content == "r1"
    assert binarized[2].content == "p2"

def test_binarize_chat_no_injection():
    """Tests that no fillers are injected."""
    fmt = SeparatorBinarizationFormat()
    chat = ChatThread([ChatMessage(ChatIntent.PROMPT, "p1")])

    binarized = fmt.binarize_chat(chat)
    assert len(binarized) == 1
    assert binarized[0].intent == ChatIntent.PROMPT
    assert binarized[0].content == "p1"

def test_binarize_chat_empty():
    """Tests binarizing an empty chat."""
    fmt = SeparatorBinarizationFormat()
    chat = ChatThread()
    assert len(fmt.binarize_chat(chat)) == 0

def test_binarize_chat_default_separator():
    """Tests that default separator is used."""
    fmt = SeparatorBinarizationFormat()
    chat = ChatThread([
        ChatMessage(ChatIntent.SYSTEM, "sys"),
        ChatMessage(ChatIntent.PROMPT, "p1"),
    ])

    binarized = fmt.binarize_chat(chat)
    assert len(binarized) == 1
    # Different original intents (SYSTEM -> PROMPT, PROMPT -> PROMPT) use separator
    assert binarized[0].content == "sys\n\n---\n\np1"

def test_binarize_chat_default_separator_special_merging():
    """Tests that default separator preserves special merging rules for SYSTEM/STATUS."""
    fmt = SeparatorBinarizationFormat()
    chat = ChatThread([
        ChatMessage(ChatIntent.SYSTEM, "sys"),
        ChatMessage(ChatIntent.STATUS, "stat"),
        ChatMessage(ChatIntent.PROMPT, "p1"),
    ])

    binarized = fmt.binarize_chat(chat)
    assert len(binarized) == 1
    # SYSTEM + STATUS -> merged with \n\n (special rule)
    # (Merged SYSTEM/STATUS) + PROMPT -> merged with default separator
    assert binarized[0].content == "sys\n\nstat\n\n---\n\np1"
