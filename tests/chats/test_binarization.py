from llobot.chats.branches import ChatBranch
from llobot.chats.messages import ChatMessage
from llobot.chats.intents import ChatIntent
from llobot.chats.binarization import binarize_chat, binarize_intent, binarize_message

def test_binarize_intent():
    assert binarize_intent(ChatIntent.SYSTEM) == ChatIntent.PROMPT
    assert binarize_intent(ChatIntent.SESSION) == ChatIntent.PROMPT
    assert binarize_intent(ChatIntent.EXAMPLE_PROMPT) == ChatIntent.PROMPT
    assert binarize_intent(ChatIntent.PROMPT) == ChatIntent.PROMPT
    assert binarize_intent(ChatIntent.AFFIRMATION) == ChatIntent.RESPONSE
    assert binarize_intent(ChatIntent.EXAMPLE_RESPONSE) == ChatIntent.RESPONSE
    assert binarize_intent(ChatIntent.RESPONSE) == ChatIntent.RESPONSE

def test_binarize_message():
    prompt_msg = ChatMessage(ChatIntent.SYSTEM, "content")
    binarized_prompt = binarize_message(prompt_msg)
    assert binarized_prompt.intent == ChatIntent.PROMPT
    assert binarized_prompt.content == "content"
    response_msg = ChatMessage(ChatIntent.AFFIRMATION, "content")
    binarized_response = binarize_message(response_msg)
    assert binarized_response.intent == ChatIntent.RESPONSE
    assert binarized_response.content == "content"

def test_binarize_chat_empty():
    branch = ChatBranch()
    assert binarize_chat(branch).messages == []
    assert binarize_chat(branch, last=ChatIntent.PROMPT).messages == [ChatMessage(ChatIntent.PROMPT, "Go on")]
    assert binarize_chat(branch, last=ChatIntent.RESPONSE).messages == [ChatMessage(ChatIntent.RESPONSE, "Okay")]

def test_binarize_chat_reorders_prompt_session():
    branch = ChatBranch([
        ChatMessage(ChatIntent.PROMPT, "p1"),
        ChatMessage(ChatIntent.SESSION, "s1"),
    ])
    binarized = binarize_chat(branch)
    assert binarized.messages == [
        ChatMessage(ChatIntent.PROMPT, "s1"),
        ChatMessage(ChatIntent.RESPONSE, "Okay"),
        ChatMessage(ChatIntent.PROMPT, "p1"),
    ]

def test_binarize_chat_reorders_prompt_session_at_end():
    branch = ChatBranch([
        ChatMessage(ChatIntent.RESPONSE, "r1"),
        ChatMessage(ChatIntent.PROMPT, "p1"),
        ChatMessage(ChatIntent.SESSION, "s1"),
    ])
    binarized = binarize_chat(branch)
    assert binarized.messages == [
        ChatMessage(ChatIntent.RESPONSE, "r1"),
        ChatMessage(ChatIntent.PROMPT, "s1"),
        ChatMessage(ChatIntent.RESPONSE, "Okay"),
        ChatMessage(ChatIntent.PROMPT, "p1"),
    ]

def test_binarize_chat_consecutive_prompts():
    branch = ChatBranch([
        ChatMessage(ChatIntent.PROMPT, "p1"),
        ChatMessage(ChatIntent.SYSTEM, "s1"),
    ])
    binarized = binarize_chat(branch)
    assert binarized.messages == [
        ChatMessage(ChatIntent.PROMPT, "p1"),
        ChatMessage(ChatIntent.RESPONSE, "Okay"),
        ChatMessage(ChatIntent.PROMPT, "s1"),
    ]

def test_binarize_chat_consecutive_responses():
    branch = ChatBranch([
        ChatMessage(ChatIntent.RESPONSE, "r1"),
        ChatMessage(ChatIntent.AFFIRMATION, "a1"),
    ])
    binarized = binarize_chat(branch)
    assert binarized.messages == [
        ChatMessage(ChatIntent.RESPONSE, "r1"),
        ChatMessage(ChatIntent.PROMPT, "Go on"),
        ChatMessage(ChatIntent.RESPONSE, "a1"),
    ]

def test_binarize_chat_last_prompt():
    branch = ChatBranch([ChatMessage(ChatIntent.PROMPT, "p1")])
    assert binarize_chat(branch, last=ChatIntent.PROMPT).messages == [ChatMessage(ChatIntent.PROMPT, "p1")]

    branch = ChatBranch([ChatMessage(ChatIntent.RESPONSE, "r1")])
    binarized = binarize_chat(branch, last=ChatIntent.PROMPT)
    assert binarized.messages == [
        ChatMessage(ChatIntent.RESPONSE, "r1"),
        ChatMessage(ChatIntent.PROMPT, "Go on"),
    ]

def test_binarize_chat_last_response():
    branch = ChatBranch([ChatMessage(ChatIntent.RESPONSE, "r1")])
    assert binarize_chat(branch, last=ChatIntent.RESPONSE).messages == [ChatMessage(ChatIntent.RESPONSE, "r1")]

    branch = ChatBranch([ChatMessage(ChatIntent.PROMPT, "p1")])
    binarized = binarize_chat(branch, last=ChatIntent.RESPONSE)
    assert binarized.messages == [
        ChatMessage(ChatIntent.PROMPT, "p1"),
        ChatMessage(ChatIntent.RESPONSE, "Okay"),
    ]

def test_binarize_chat_complex_case():
    branch = ChatBranch([
        ChatMessage(ChatIntent.SYSTEM, "system"),
        ChatMessage(ChatIntent.PROMPT, "p1"),
        ChatMessage(ChatIntent.SESSION, "s1"),
        ChatMessage(ChatIntent.RESPONSE, "r1"),
        ChatMessage(ChatIntent.AFFIRMATION, "a1"),
    ])
    binarized = binarize_chat(branch, last=ChatIntent.PROMPT)
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
