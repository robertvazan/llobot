from llobot.chats.intents import ChatIntent
from llobot.chats.messages import ChatMessage

def test_properties():
    """Tests basic properties of ChatMessage."""
    msg = ChatMessage(ChatIntent.PROMPT, "Hello")
    assert msg.intent == ChatIntent.PROMPT
    assert msg.content == "Hello"
    assert msg.cost == len("Hello") + 10

def test_equality():
    """Tests equality and hashing."""
    msg1 = ChatMessage(ChatIntent.PROMPT, "Hello")
    msg2 = ChatMessage(ChatIntent.PROMPT, "Hello")
    msg3 = ChatMessage(ChatIntent.RESPONSE, "Hello")
    msg4 = ChatMessage(ChatIntent.PROMPT, "World")

    assert msg1 == msg2
    assert msg1 != msg3
    assert msg1 != msg4
    assert len({msg1, msg2, msg3, msg4}) == 3

def test_contains():
    """Tests the 'in' operator."""
    msg = ChatMessage(ChatIntent.PROMPT, "Hello world")
    assert "Hello" in msg
    assert "world" in msg
    assert "foo" not in msg

def test_branch():
    """Tests converting a message to a branch."""
    from llobot.chats.branches import ChatBranch
    msg = ChatMessage(ChatIntent.PROMPT, "Hello")
    branch = msg.branch()
    assert isinstance(branch, ChatBranch)
    assert len(branch) == 1
    assert branch[0] == msg

def test_with_intent():
    """Tests changing the intent of a message."""
    msg = ChatMessage(ChatIntent.PROMPT, "Hello")
    new_msg = msg.with_intent(ChatIntent.RESPONSE)
    assert new_msg.intent == ChatIntent.RESPONSE
    assert new_msg.content == "Hello"
    assert msg.intent == ChatIntent.PROMPT # Original is unchanged

def test_as_example():
    """Tests converting a message to an example message."""
    prompt = ChatMessage(ChatIntent.PROMPT, "Question")
    example_prompt = prompt.as_example()
    assert example_prompt.intent == ChatIntent.EXAMPLE_PROMPT
    assert example_prompt.content == "Question"

    response = ChatMessage(ChatIntent.RESPONSE, "Answer")
    example_response = response.as_example()
    assert example_response.intent == ChatIntent.EXAMPLE_RESPONSE
    assert example_response.content == "Answer"

def test_monolithic():
    """Tests the monolithic string representation."""
    msg = ChatMessage(ChatIntent.PROMPT, "Hello")
    assert msg.monolithic() == "**Prompt:**\n\nHello"

def test_with_content():
    """Tests changing the content of a message."""
    msg = ChatMessage(ChatIntent.PROMPT, "Hello")
    new_msg = msg.with_content("World")
    assert new_msg.intent == ChatIntent.PROMPT
    assert new_msg.content == "World"
    assert msg.content == "Hello" # Original is unchanged

def test_with_postscript():
    """Tests appending a postscript to the message content."""
    msg = ChatMessage(ChatIntent.PROMPT, "Hello")

    # Postscript on non-empty content
    with_ps = msg.with_postscript("World")
    assert with_ps.content == "Hello\n\nWorld"

    # Empty postscript
    with_empty_ps = msg.with_postscript("")
    assert with_empty_ps.content == "Hello"

    # Postscript on empty content
    empty_msg = ChatMessage(ChatIntent.PROMPT, "")
    with_ps_on_empty = empty_msg.with_postscript("World")
    assert with_ps_on_empty.content == "World"
