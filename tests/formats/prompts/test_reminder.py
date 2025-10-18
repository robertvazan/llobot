from llobot.formats.prompts.reminder import ReminderPromptFormat
from llobot.chats.intent import ChatIntent

def test_render():
    formatter = ReminderPromptFormat()
    prompt = "- IMPORTANT: one\n- other\n- IMPORTANT: two"
    content = formatter.render(prompt)
    assert 'Reminder:' in content
    assert '- one' in content
    assert '- two' in content
    assert 'other' not in content

def test_render_no_reminders():
    formatter = ReminderPromptFormat()
    prompt = "No important messages here."
    assert formatter.render(prompt) == ""

def test_render_chat():
    formatter = ReminderPromptFormat()
    prompt = "- IMPORTANT: one\n- other\n- IMPORTANT: two"
    chat = formatter.render_chat(prompt)
    assert len(chat) == 2
    assert chat[0].intent == ChatIntent.SYSTEM
    content = chat[0].content
    assert 'Reminder:' in content
    assert '- one' in content
    assert '- two' in content
    assert 'other' not in content

def test_render_chat_no_reminders():
    formatter = ReminderPromptFormat()
    prompt = "No important messages here."
    chat = formatter.render_chat(prompt)
    assert not chat
