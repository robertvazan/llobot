import base64
import hashlib
from pathlib import Path
from textwrap import dedent
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.stream import record_stream
from llobot.chats.thread import ChatThread
from llobot.models.echo import EchoModel
from llobot.roles.agent import Agent
from llobot.tools.write import WriteTool

def get_response_content(thread: ChatThread) -> str:
    """Helper to extract model response content from the thread."""
    for msg in thread:
        if msg.intent == ChatIntent.RESPONSE:
            return msg.content
    return ""

def get_session_hash(prompt: ChatThread) -> str:
    """Helper to compute session hash from a prompt thread."""
    if not prompt or not prompt[0].content:
        raise ValueError("Cannot compute hash for empty initial prompt")
    hasher = hashlib.sha256(prompt[0].content.encode('utf-8'))
    b64 = base64.urlsafe_b64encode(hasher.digest()).decode('ascii')
    return b64[:40]

def test_agent_first_turn(tmp_path: Path):
    """Tests that Agent creates a new session and includes system prompt on first turn."""
    model = EchoModel('echo')
    agent = Agent('agent', model, prompt="You are an agent.", session_history=tmp_path)

    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "Hello")])
    stream = agent.chat(prompt)
    record_stream(stream)

    # Check that session history was created
    session_hash = get_session_hash(prompt)
    assert (tmp_path / session_hash).exists()

def test_agent_session_persistence(tmp_path: Path):
    """Tests that Agent can resume a session and load persisted state."""
    model = EchoModel('echo')

    # First turn: create a session
    agent1 = Agent('agent', model, prompt="System", session_history=tmp_path)
    prompt1 = ChatThread([ChatMessage(ChatIntent.PROMPT, "First")])
    record_stream(agent1.chat(prompt1))  # this will save the session

    # Second turn: resume the session with a custom agent that verifies state loading
    class StatefulAgent(Agent):
        def handle_setup(self, env):
            super().handle_setup(env)
            from llobot.environments.status import StatusEnv
            env[StatusEnv].append("State loaded.")

    agent2 = StatefulAgent('stateful', model, session_history=tmp_path)
    # The prompt is the full history. The agent uses the first message to find the session.
    prompt2 = ChatThread([
        ChatMessage(ChatIntent.PROMPT, "First"),
        ChatMessage(ChatIntent.RESPONSE, "Some response from turn 1"),
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
    record_stream(agent.chat(prompt1))
    # Session for "Original" is created and saved.

    # Turn 2: User edits history within the same session.
    prompt2 = ChatThread([
        ChatMessage(ChatIntent.PROMPT, "Original"), # Same initial prompt to stay in session
        ChatMessage(ChatIntent.PROMPT, "Edited"), # This replaces what was in the second turn
        ChatMessage(ChatIntent.RESPONSE, "New Response"), # User fabricated a response
        ChatMessage(ChatIntent.PROMPT, "Next")
    ])

    # Agent should load context from session "Original", then detect mismatch,
    # truncate, and append the new history.
    stream2 = agent.chat(prompt2)
    response2 = get_response_content(record_stream(stream2))

    # The EchoModel echoes the context. We expect "Edited" to be present, and the response from turn 1 to be gone.
    assert "Edited" in response2
    assert "Original" in response2 # The first prompt is still there
    assert "New Response" in response2

def test_agent_accept_command(tmp_path: Path):
    """Tests that Agent can execute tool calls with @accept command."""
    model = EchoModel('echo')
    # Agent needs a project to write files to.
    from llobot.projects.directory import DirectoryProject
    project = DirectoryProject(tmp_path / 'project', mutable=True)
    from llobot.projects.library.zone import ZoneKeyedProjectLibrary
    library = ZoneKeyedProjectLibrary(project)

    # Agent base class doesn't handle project commands by default. We add it for this test.
    class ProjectAwareAgent(Agent):
        def handle_setup(self, env):
            super().handle_setup(env)
            from llobot.commands.project import handle_project_commands
            handle_project_commands(env)

    agent = ProjectAwareAgent('agent', model, tools=[WriteTool()], session_history=tmp_path / 'sessions', projects=library)

    file_tool_call_str = dedent("""\
        <details>
        <summary>Write: ~/project/test.txt</summary>

        ```
        content
        ```

        </details>""")

    # A project must be selected for its files to be writable.
    prompt = ChatThread([
        ChatMessage(ChatIntent.PROMPT, "Initial prompt"),
        ChatMessage(ChatIntent.RESPONSE, file_tool_call_str),
        ChatMessage(ChatIntent.PROMPT, "@project @accept"),
    ])

    stream = agent.chat(prompt)
    response_thread = record_stream(stream)

    status_msg = next((m for m in response_thread if m.intent == ChatIntent.STATUS), None)
    assert status_msg
    assert "✅ All 1 tool calls executed." in status_msg.content
    assert "Success: write ~/project/test.txt" in status_msg.content
    assert (tmp_path / 'project/test.txt').read_text().strip() == 'content'
