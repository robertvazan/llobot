from llobot.formats.prompts.plain import PlainPromptFormat
from llobot.chats.intent import ChatIntent

def test_render():
    formatter = PlainPromptFormat()
    assert formatter.render("System prompt.") == "System prompt."
    assert formatter.render("") == ""

def test_render_chat():
    formatter = PlainPromptFormat()
    chat = formatter.render_chat("System prompt.")
    assert len(chat) == 1
    assert chat[0].intent == ChatIntent.SYSTEM
    assert chat[0].content == "System prompt."

def test_render_chat_empty():
    formatter = PlainPromptFormat()
    chat = formatter.render_chat("")
    assert not chat
