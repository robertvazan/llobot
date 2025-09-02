from llobot.chats import ChatBranch, ChatMessage, ChatIntent

def test_binarize_empty():
    branch = ChatBranch()
    assert branch.binarize().messages == []
    assert branch.binarize(last=ChatIntent.PROMPT).messages == [ChatMessage(ChatIntent.PROMPT, "Go on")]
    assert branch.binarize(last=ChatIntent.RESPONSE).messages == [ChatMessage(ChatIntent.RESPONSE, "Okay")]

def test_binarize_reorders_prompt_session():
    branch = ChatBranch([
        ChatMessage(ChatIntent.PROMPT, "p1"),
        ChatMessage(ChatIntent.SESSION, "s1"),
    ])
    binarized = branch.binarize()
    assert binarized.messages == [
        ChatMessage(ChatIntent.PROMPT, "s1"),
        ChatMessage(ChatIntent.RESPONSE, "Okay"),
        ChatMessage(ChatIntent.PROMPT, "p1"),
    ]

def test_binarize_reorders_prompt_session_at_end():
    branch = ChatBranch([
        ChatMessage(ChatIntent.RESPONSE, "r1"),
        ChatMessage(ChatIntent.PROMPT, "p1"),
        ChatMessage(ChatIntent.SESSION, "s1"),
    ])
    binarized = branch.binarize()
    assert binarized.messages == [
        ChatMessage(ChatIntent.RESPONSE, "r1"),
        ChatMessage(ChatIntent.PROMPT, "s1"),
        ChatMessage(ChatIntent.RESPONSE, "Okay"),
        ChatMessage(ChatIntent.PROMPT, "p1"),
    ]

def test_binarize_consecutive_prompts():
    branch = ChatBranch([
        ChatMessage(ChatIntent.PROMPT, "p1"),
        ChatMessage(ChatIntent.SYSTEM, "s1"),
    ])
    binarized = branch.binarize()
    assert binarized.messages == [
        ChatMessage(ChatIntent.PROMPT, "p1"),
        ChatMessage(ChatIntent.RESPONSE, "Okay"),
        ChatMessage(ChatIntent.PROMPT, "s1"),
    ]

def test_binarize_consecutive_responses():
    branch = ChatBranch([
        ChatMessage(ChatIntent.RESPONSE, "r1"),
        ChatMessage(ChatIntent.AFFIRMATION, "a1"),
    ])
    binarized = branch.binarize()
    assert binarized.messages == [
        ChatMessage(ChatIntent.RESPONSE, "r1"),
        ChatMessage(ChatIntent.PROMPT, "Go on"),
        ChatMessage(ChatIntent.RESPONSE, "a1"),
    ]

def test_binarize_last_prompt():
    branch = ChatBranch([ChatMessage(ChatIntent.PROMPT, "p1")])
    assert branch.binarize(last=ChatIntent.PROMPT).messages == [ChatMessage(ChatIntent.PROMPT, "p1")]

    branch = ChatBranch([ChatMessage(ChatIntent.RESPONSE, "r1")])
    binarized = branch.binarize(last=ChatIntent.PROMPT)
    assert binarized.messages == [
        ChatMessage(ChatIntent.RESPONSE, "r1"),
        ChatMessage(ChatIntent.PROMPT, "Go on"),
    ]

def test_binarize_last_response():
    branch = ChatBranch([ChatMessage(ChatIntent.RESPONSE, "r1")])
    assert branch.binarize(last=ChatIntent.RESPONSE).messages == [ChatMessage(ChatIntent.RESPONSE, "r1")]

    branch = ChatBranch([ChatMessage(ChatIntent.PROMPT, "p1")])
    binarized = branch.binarize(last=ChatIntent.RESPONSE)
    assert binarized.messages == [
        ChatMessage(ChatIntent.PROMPT, "p1"),
        ChatMessage(ChatIntent.RESPONSE, "Okay"),
    ]

def test_binarize_complex_case():
    branch = ChatBranch([
        ChatMessage(ChatIntent.SYSTEM, "system"),
        ChatMessage(ChatIntent.PROMPT, "p1"),
        ChatMessage(ChatIntent.SESSION, "s1"),
        ChatMessage(ChatIntent.RESPONSE, "r1"),
        ChatMessage(ChatIntent.AFFIRMATION, "a1"),
    ])
    binarized = branch.binarize(last=ChatIntent.PROMPT)
    assert binarized.messages == [
        ChatMessage(ChatIntent.PROMPT, "system"),
        ChatMessage(ChatIntent.RESPONSE, "Okay"),
        ChatMessage(ChatIntent.PROMPT, "s1"),
        ChatMessage(ChatIntent.RESPONSE, "Okay"),
        ChatMessage(ChatIntent.PROMPT, "p1"),
        ChatMessage(ChatIntent.RESPONSE, "r1"),
        ChatMessage(ChatIntent.PROMPT, "Go on"),
        ChatMessage(ChatIntent.RESPONSE, "a1"),
        ChatMessage(ChatIntent.PROMPT, "Go on"),
    ]
