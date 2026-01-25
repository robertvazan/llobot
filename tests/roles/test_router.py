import pytest
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.thread import ChatThread
from llobot.roles import Role
from llobot.roles.router import Router

class MockRole(Role):
    def __init__(self, name: str):
        self._name = name
        self.last_prompt: ChatThread | None = None

    @property
    def name(self) -> str:
        return self._name

    def chat(self, prompt: ChatThread):
        self.last_prompt = prompt
        yield ChatIntent.RESPONSE
        yield f"Hello from {self.name}"

def test_router_init_duplicates():
    role1 = MockRole("role1")
    role2 = MockRole("role1")
    with pytest.raises(ValueError, match="Duplicate role name: role1"):
        Router([role1, role2])

def test_router_routing():
    role1 = MockRole("role1")
    role2 = MockRole("role2")
    router = Router([role1, role2])

    # Test routing to role1
    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "@role1 hello")])
    response = list(router.chat(prompt))
    assert response == [ChatIntent.RESPONSE, "Hello from role1"]
    assert role1.last_prompt is not None
    assert role1.last_prompt[0].content.strip() == "hello"
    assert role2.last_prompt is None

    # Test routing to role2
    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "hey @role2")])
    response = list(router.chat(prompt))
    assert response == [ChatIntent.RESPONSE, "Hello from role2"]
    assert role2.last_prompt is not None
    assert role2.last_prompt[0].content.strip() == "hey"

def test_router_filtering():
    coder = MockRole("coder")
    router = Router([coder])

    # Mention with other text
    prompt = ChatThread([
        ChatMessage(ChatIntent.PROMPT, "@coder make this code better"),
        ChatMessage(ChatIntent.PROMPT, "follow up")
    ])
    list(router.chat(prompt))

    received = coder.last_prompt
    assert received is not None
    assert len(received) == 2
    assert received[0].content.strip() == "make this code better"
    assert received[1].content == "follow up"

    # Multiple mentions of the same role (should be treated as one target)
    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "@coder please help @coder")])
    list(router.chat(prompt))
    assert coder.last_prompt is not None
    assert coder.last_prompt[0].content.strip() == "please help"

def test_router_errors():
    role1 = MockRole("role1")
    router = Router([role1])

    # No target
    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "hello")])
    with pytest.raises(ValueError, match="Expected exactly one target role, found 0"):
        list(router.chat(prompt))

    # Unknown target
    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "@unknown hello")])
    with pytest.raises(ValueError, match="Expected exactly one target role, found 0"):
        list(router.chat(prompt))

    # Multiple targets
    role2 = MockRole("role2")
    router = Router([role1, role2])
    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "@role1 @role2 hello")])
    with pytest.raises(ValueError, match="Expected exactly one target role, found 2"):
        list(router.chat(prompt))

    # Empty prompt
    prompt = ChatThread([])
    with pytest.raises(ValueError, match="Prompt is empty"):
        list(router.chat(prompt))

def test_router_sticky_routing():
    # Router only checks the first message
    role1 = MockRole("role1")
    role2 = MockRole("role2")
    router = Router([role1, role2])

    prompt = ChatThread([
        ChatMessage(ChatIntent.PROMPT, "@role1 start"),
        ChatMessage(ChatIntent.RESPONSE, "ok"),
        ChatMessage(ChatIntent.PROMPT, "@role2 switch?") # This mention is in 3rd message
    ])

    list(router.chat(prompt))

    # Should route to role1 because it's in the first message
    assert role1.last_prompt is not None

    # Verify that @role2 was NOT filtered because it wasn't the target role mention in the first message
    # Router filters "target_name" from "first_message". It does not touch subsequent messages.
    assert role1.last_prompt[2].content == "@role2 switch?"
