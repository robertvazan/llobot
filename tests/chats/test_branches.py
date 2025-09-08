from llobot.chats.intents import ChatIntent
from llobot.chats.messages import ChatMessage
from llobot.chats.branches import ChatBranch

def test_construction_and_properties():
    """Tests ChatBranch construction and basic properties."""
    msg1 = ChatMessage(ChatIntent.PROMPT, "p1")
    msg2 = ChatMessage(ChatIntent.RESPONSE, "r1")
    branch = ChatBranch([msg1, msg2])

    assert len(branch) == 2
    assert branch.messages == [msg1, msg2]
    assert bool(branch) is True
    assert branch.cost == msg1.cost + msg2.cost

    empty_branch = ChatBranch()
    assert len(empty_branch) == 0
    assert bool(empty_branch) is False

def test_equality_and_hashing():
    """Tests equality and hashing of ChatBranch."""
    msg1 = ChatMessage(ChatIntent.PROMPT, "p1")
    msg2 = ChatMessage(ChatIntent.RESPONSE, "r1")
    branch1 = ChatBranch([msg1, msg2])
    branch2 = ChatBranch([msg1, msg2])
    branch3 = ChatBranch([msg1])

    assert branch1 == branch2
    assert branch1 != branch3
    assert len({branch1, branch2, branch3}) == 2

def test_indexing_and_slicing():
    """Tests item access and slicing."""
    msg1 = ChatMessage(ChatIntent.PROMPT, "p1")
    msg2 = ChatMessage(ChatIntent.RESPONSE, "r1")
    msg3 = ChatMessage(ChatIntent.PROMPT, "p2")
    branch = ChatBranch([msg1, msg2, msg3])

    assert branch[0] == msg1
    assert branch[-1] == msg3

    slice = branch[1:3]
    assert isinstance(slice, ChatBranch)
    assert slice.messages == [msg2, msg3]

def test_iteration_and_containment():
    """Tests iteration and 'in' operator."""
    msg1 = ChatMessage(ChatIntent.PROMPT, "Hello")
    msg2 = ChatMessage(ChatIntent.RESPONSE, "World")
    branch = ChatBranch([msg1, msg2])

    assert list(branch) == [msg1, msg2]
    assert "Hello" in branch
    assert "World" in branch
    assert "foo" not in branch

def test_addition():
    """Tests concatenation of branches and messages."""
    msg1 = ChatMessage(ChatIntent.PROMPT, "p1")
    msg2 = ChatMessage(ChatIntent.RESPONSE, "r1")
    branch1 = ChatBranch([msg1])
    branch2 = ChatBranch([msg2])

    combined = branch1 + branch2
    assert combined.messages == [msg1, msg2]

    combined_with_msg = branch1 + msg2
    assert combined_with_msg.messages == [msg1, msg2]

    combined_with_none = branch1 + None
    assert combined_with_none == branch1

def test_monolithic():
    """Tests monolithic string representation of a branch."""
    msg1 = ChatMessage(ChatIntent.PROMPT, "p1")
    msg2 = ChatMessage(ChatIntent.RESPONSE, "r1")
    branch = ChatBranch([msg1, msg2])

    expected = "**Prompt:**\n\np1\n\n**Response:**\n\nr1"
    assert branch.monolithic() == expected

def test_common_prefix():
    """Tests finding the common prefix with the '&' operator."""
    msg1 = ChatMessage(ChatIntent.PROMPT, "p1")
    msg2 = ChatMessage(ChatIntent.RESPONSE, "r1")
    msg3 = ChatMessage(ChatIntent.PROMPT, "p2")
    msg4 = ChatMessage(ChatIntent.PROMPT, "p3")

    branch1 = ChatBranch([msg1, msg2, msg3])
    branch2 = ChatBranch([msg1, msg2, msg4])
    branch3 = ChatBranch([msg1])

    prefix = branch1 & branch2
    assert prefix.messages == [msg1, msg2]

    prefix2 = branch1 & branch3
    assert prefix2.messages == [msg1]

    prefix3 = branch1 & ChatBranch()
    assert len(prefix3) == 0
