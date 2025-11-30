import re
from pathlib import Path
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.stream import record_stream
from llobot.chats.thread import ChatThread
from llobot.models.echo import EchoModel
from llobot.roles.agent import Agent

def get_response_content(thread: ChatThread) -> str:
    """Helper to extract model response content from the thread."""
    for msg in thread:
        if msg.intent == ChatIntent.RESPONSE:
            return msg.content
    return ""

def extract_session_id(thread: ChatThread) -> str:
    """Helper to extract session ID from the thread."""
    session_msg = next((m for m in thread if m.intent == ChatIntent.SESSION), None)
    assert session_msg, "No SESSION message found"
    session_match = re.search(r'Session: @(\d{8}-\d{6})', session_msg.content)
    assert session_match, "No session ID found in SESSION message"
    return session_match.group(1)

def test_agent_first_turn(tmp_path: Path):
    """Tests that Agent creates a new session and includes system prompt on first turn."""
    model = EchoModel('echo')
    agent = Agent('agent', model, prompt="You are an agent.", session_history=tmp_path)

    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "Hello")])
    stream = agent.chat(prompt)
    response_thread = record_stream(stream)
    response_content = get_response_content(response_thread)

    # Check that system prompt and reminder are present
    assert "You are an agent." in response_content
    assert "Hello" in response_content

    # Check that session ID was assigned
    session_id = extract_session_id(response_thread)
    assert session_id

    # Check that session history was created
    assert any(tmp_path.iterdir())

def test_agent_session_persistence(tmp_path: Path):
    """Tests that Agent can resume a session and load persisted state."""
    model = EchoModel('echo')

    # First turn: create a session
    agent1 = Agent('agent', model, prompt="System", session_history=tmp_path)
    prompt1 = ChatThread([ChatMessage(ChatIntent.PROMPT, "First")])
    thread1 = record_stream(agent1.chat(prompt1))
    session_id = extract_session_id(thread1)

    # Second turn: resume the session with a custom agent that verifies state loading
    class StatefulAgent(Agent):
        def handle_commands(self, env):
            from llobot.environments.status import StatusEnv
            env[StatusEnv].append("State loaded.")

    agent2 = StatefulAgent('stateful', model, session_history=tmp_path)
    prompt2 = ChatThread([
        ChatMessage(ChatIntent.SESSION, f"Session: @{session_id}"),
        ChatMessage(ChatIntent.PROMPT, "Next")
    ])

    stream2 = agent2.chat(prompt2)
    response_thread2 = record_stream(stream2)

    # The status message should be present
    status_msg = next((m for m in response_thread2 if m.intent == ChatIntent.STATUS), None)
    assert status_msg
    assert "State loaded." in status_msg.content

def test_agent_reminder(tmp_path: Path):
    """Tests that Agent includes a reminder prompt on first turn."""
    model = EchoModel('echo')
    agent = Agent('agent', model, prompt="System.\n- IMPORTANT: Do this.", session_history=tmp_path)

    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "Hi")])
    response = get_response_content(record_stream(agent.chat(prompt)))

    # Reminder should be extracted and included
    assert "Reminder:" in response
    assert "- Do this." in response

def test_agent_coercion(tmp_path: Path):
    """Tests that Agent coerces context to match altered history."""
    model = EchoModel('echo')
    agent = Agent('agent', model, prompt="System", session_history=tmp_path)

    # Turn 1
    prompt1 = ChatThread([ChatMessage(ChatIntent.PROMPT, "Original")])
    thread1 = record_stream(agent.chat(prompt1))
    session_id = extract_session_id(thread1)
    # thread1 content: [System, Reminder, Prompt(Original), Session, Response(Original)]

    # Turn 2: User edits "Original" to "Edited" in the history
    prompt2 = ChatThread([
        ChatMessage(ChatIntent.SESSION, f"Session: @{session_id}"), # Reused session
        ChatMessage(ChatIntent.PROMPT, "Edited"), # This replaces "Original" in user's view
        ChatMessage(ChatIntent.RESPONSE, "New Response"), # User fabricated a response
        ChatMessage(ChatIntent.PROMPT, "Next")
    ])

    # Agent should detect mismatch in history (Original vs Edited), truncate context, and append Edited.
    stream2 = agent.chat(prompt2)
    response2 = get_response_content(record_stream(stream2))

    # The EchoModel echoes the context. We expect "Edited" to be present, and "Original" to be gone.
    assert "Edited" in response2
    assert "Original" not in response2
    assert "New Response" in response2
