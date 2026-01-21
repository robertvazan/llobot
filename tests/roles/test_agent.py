from pathlib import Path
from textwrap import dedent
from pytest import raises
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.stream import record_stream
from llobot.chats.thread import ChatThread
from llobot.environments.projects import ProjectEnv
from tests.models.mock import MockModel
from llobot.roles.agent import Agent
from llobot.tools.write import WriteTool
from llobot.environments.prompt import _hash_thread
from llobot.chats.markdown import save_chat_to_markdown

def test_agent_first_turn(tmp_path: Path):
    """Tests that Agent creates a new session and includes system prompt on first turn."""
    model = MockModel('echo')
    agent = Agent('agent', model, prompt="You are an agent.", session_history=tmp_path)

    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "Hello")])
    stream = agent.chat(prompt)
    record_stream(stream)

    # We save under hash(prompt)
    session_hash = _hash_thread(prompt)

    # Check that session history was created
    assert (tmp_path / session_hash).exists()

def test_agent_session_persistence(tmp_path: Path):
    """Tests that Agent can resume a session and load persisted state."""
    model = MockModel('echo')

    # Turn 1: create a session
    agent1 = Agent('agent', model, prompt="System", session_history=tmp_path)
    prompt1 = ChatThread([ChatMessage(ChatIntent.PROMPT, "First")])
    response1 = record_stream(agent1.chat(prompt1))

    # Turn 2: resume the session.
    # The prompt is [P1, R1, P2]. Previous hash = hash([P1]).
    # We saved Turn 1 under hash([P1]). So this should work.
    prompt2 = prompt1 + response1 + ChatMessage(ChatIntent.PROMPT, "Next")

    class StatefulAgent(Agent):
        def handle_setup(self, env):
            super().handle_setup(env)
            from llobot.environments.context import ContextEnv
            env[ContextEnv].add(ChatMessage(ChatIntent.STATUS, "State loaded."))

    agent2 = StatefulAgent('stateful', model, session_history=tmp_path)
    stream2 = agent2.chat(prompt2)
    response_thread2 = record_stream(stream2)

    # The status message should be present
    status_msg = next((m for m in response_thread2 if m.intent == ChatIntent.STATUS), None)
    assert status_msg
    assert "State loaded." in status_msg.content

def test_agent_reminder(tmp_path: Path):
    """Tests that Agent includes a reminder prompt on first turn."""
    model = MockModel('echo')
    agent = Agent('agent', model, prompt="System.\n- IMPORTANT: Do this.", session_history=tmp_path)

    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "Hi")])
    record_stream(agent.chat(prompt))

    context = model.history[0]

    # Reminder should be extracted and included
    assert "Reminder:" in context
    assert "- Do this." in context

def test_agent_branching(tmp_path: Path):
    """Tests that Agent branches context correctly."""
    model = MockModel('echo')
    agent = Agent('agent', model, prompt="System", session_history=tmp_path)

    # Turn 1
    prompt1 = ChatThread([ChatMessage(ChatIntent.PROMPT, "Original")])
    response1 = record_stream(agent.chat(prompt1))
    # Session S1 is saved for [Original].

    # Turn 2: User branches off from Turn 1.
    prompt2 = prompt1 + response1 + ChatMessage(ChatIntent.PROMPT, "Branch A")
    record_stream(agent.chat(prompt2))
    # Agent loads S1 (hash(Original)), generates Response A.
    # Session S2 is saved for [Original, Response1, Branch A].

    # Turn 2 (Alternative): User branches off differently from Turn 1.
    prompt3 = prompt1 + response1 + ChatMessage(ChatIntent.PROMPT, "Branch B")
    record_stream(agent.chat(prompt3))
    # Agent loads S1 (it's still there), generates Response B.
    # Session S3 is saved for [Original, Response1, Branch B].

    # Verify that S1 exists.
    assert (tmp_path / _hash_thread(prompt1)).exists()

    # Verify S2 and S3 exist
    assert (tmp_path / _hash_thread(prompt2)).exists()
    assert (tmp_path / _hash_thread(prompt3)).exists()

def test_agent_missing_history(tmp_path: Path):
    """Tests that Agent raises FileNotFoundError when history is missing."""
    model = MockModel('echo')
    agent = Agent('agent', model, prompt="System", session_history=tmp_path)

    # Construct a prompt that looks like a second turn (P1, R1, P2)
    # but where the first turn (P1) was never saved.
    prompt = ChatThread([
        ChatMessage(ChatIntent.PROMPT, "Ghost"),
        ChatMessage(ChatIntent.RESPONSE, "Woo"),
        ChatMessage(ChatIntent.PROMPT, "Buster")
    ])

    with raises(FileNotFoundError, match="Previous session .* not found"):
        list(agent.chat(prompt))

def test_agent_accept_command(tmp_path: Path):
    """Tests that Agent can execute tool calls with @accept command."""
    model = MockModel('echo')
    # Agent needs a project to write files to.
    from llobot.projects.directory import DirectoryProject
    project = DirectoryProject(tmp_path / 'project', prefix="project", mutable=True)
    from llobot.projects.library.predefined import PredefinedProjectLibrary
    library = PredefinedProjectLibrary({'project': project})

    # Agent base class doesn't handle project commands by default. We add it for this test.
    class ProjectAwareAgent(Agent):
        def handle_setup(self, env):
            super().handle_setup(env)
            from llobot.commands.project import handle_project_commands
            handle_project_commands(env)

    agent = ProjectAwareAgent('agent', model, tools=[WriteTool()], session_history=tmp_path / 'sessions', projects=library)

    file_tool_call_str = dedent("""\
        <details>
        <summary>write: ~/project/test.txt</summary>

        ```
        content
        ```

        </details>""")

    first_turn_thread = ChatThread([
        ChatMessage(ChatIntent.PROMPT, "Initial prompt"),
        ChatMessage(ChatIntent.RESPONSE, file_tool_call_str)
    ])

    # Create the session state for the first turn (hash of [P1])
    session_hash = _hash_thread(first_turn_thread[0:1])
    session_dir = tmp_path / 'sessions' / session_hash
    session_dir.mkdir(parents=True)

    # Save the context that includes the response with the tool call
    save_chat_to_markdown(session_dir / 'context.md', first_turn_thread)

    # Now the second turn
    prompt2 = first_turn_thread + ChatMessage(ChatIntent.PROMPT, "@project @accept")

    stream = agent.chat(prompt2)
    response_thread = record_stream(stream)

    # Expect two status messages: one for log, one for summary
    status_messages = [m for m in response_thread if m.intent == ChatIntent.STATUS]
    assert len(status_messages) == 2

    log_msg = status_messages[0]
    assert "Written `~/project/test.txt`" in log_msg.content

    summary_msg = status_messages[1]
    assert "✅ All 1 tool calls executed." in summary_msg.content

    assert (tmp_path / 'project/test.txt').read_text().strip() == 'content'

def test_agent_project_summary(tmp_path: Path):
    """Tests that Agent includes project summary in the context."""
    model = MockModel('echo')

    # Setup a project environment with a mock project
    from llobot.projects.marker import MarkerProject
    project = MarkerProject("myproject")
    from llobot.projects.library.predefined import PredefinedProjectLibrary
    library = PredefinedProjectLibrary({'myproject': project})

    class PreselectedAgent(Agent):
        def handle_setup(self, env):
            env[ProjectEnv].add('myproject')

    agent = PreselectedAgent('agent', model, session_history=tmp_path, projects=library)
    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "Hello")])
    record_stream(agent.chat(prompt))
    context = model.history[0]

    assert "Projects:" in context
    assert "- Marker `~/myproject`" in context

def test_agent_stuffing_order_with_setup_message(tmp_path: Path):
    """
    Tests that context stuffing prepends system prompt even if setup added messages.
    """
    model = MockModel('echo')

    class SetupAgent(Agent):
        def handle_setup(self, env):
            # Simulate setup adding a message before stuffing
            from llobot.environments.context import ContextEnv
            env[ContextEnv].add(ChatMessage(ChatIntent.STATUS, "Setup complete."))
            super().handle_setup(env)

    agent = SetupAgent('agent', model, prompt="System Prompt.", session_history=tmp_path)

    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "Hello")])
    record_stream(agent.chat(prompt))

    # Check the context sent to the model
    thread = model.history[0]
    messages = thread.messages

    # We expect:
    # 1. System Prompt (from stuff)
    # 2. Reminder (from remind, added after stuff)
    # 3. Setup complete. (from handle_setup, preserved and re-added)
    # 4. Hello (Prompt)

    # Find the index of the SYSTEM message containing "System Prompt."
    idx_system = next((i for i, m in enumerate(messages)
                       if m.intent == ChatIntent.SYSTEM and "System Prompt." in m.content), -1)

    # Find the index of the STATUS message containing "Setup complete."
    idx_setup = next((i for i, m in enumerate(messages)
                      if m.intent == ChatIntent.STATUS and "Setup complete." in m.content), -1)

    assert idx_system != -1, "System prompt not found in context"
    assert idx_setup != -1, "Setup message not found in context"
    assert idx_system < idx_setup, f"System prompt (idx={idx_system}) should be before setup messages (idx={idx_setup})."
