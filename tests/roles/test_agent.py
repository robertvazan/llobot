from pathlib import Path
from textwrap import dedent
from pytest import raises
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.stream import record_stream
from llobot.chats.thread import ChatThread
from tests.models.mock import MockModel
from llobot.roles.agent import Agent
from llobot.tools.write import WriteTool
from llobot.environments.prompt import _hash_thread
from llobot.chats.markdown import save_chat_to_markdown
from llobot.roles.autonomy import Autonomy, StepAutonomy, NoAutonomy

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

def test_agent_run_command(tmp_path: Path):
    """Tests that Agent can execute tool calls with @run command."""
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
        <summary>Write: ~/project/test.txt</summary>

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
    prompt2 = first_turn_thread + ChatMessage(ChatIntent.PROMPT, "@project @run")

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

def test_agent_autorun(tmp_path: Path):
    """Tests that Agent executes tool calls automatically when autonomy is enabled."""
    # Setup project
    from llobot.projects.directory import DirectoryProject
    project = DirectoryProject(tmp_path / 'project', prefix="project", mutable=True)
    from llobot.projects.library.predefined import PredefinedProjectLibrary
    library = PredefinedProjectLibrary({'project': project})

    # Setup model that returns a tool call
    tool_call_1 = dedent("""\
        <details>
        <summary>Write: ~/project/file1.txt</summary>

        ```
        content1
        ```

        </details>""")
    tool_call_2 = dedent("""\
        <details>
        <summary>Write: ~/project/file2.txt</summary>

        ```
        content2
        ```

        </details>""")
    # We want the model to return two messages, both with tool calls.
    # MockModel 'echo' echoes the prompt. We can simulate response by making the model return preset response?
    # MockModel doesn't support preset responses directly in 'echo' mode.
    # Let's subclass MockModel to return specific responses.

    class PresetModel(MockModel):
        def generate(self, prompt):
            self._history.append(prompt)
            yield ChatIntent.RESPONSE
            yield tool_call_1
            # Simulate a second response message
            yield ChatIntent.RESPONSE
            yield tool_call_2

    model = PresetModel('preset')

    class ProjectAwareAgent(Agent):
        def handle_setup(self, env):
            super().handle_setup(env)
            from llobot.commands.project import handle_project_commands
            handle_project_commands(env)

    # Create agent with StepAutonomy
    agent = ProjectAwareAgent(
        'agent',
        model,
        tools=[WriteTool()],
        session_history=tmp_path / 'sessions',
        projects=library,
        autonomy=StepAutonomy()
    )

    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "@project Do work")])
    stream = agent.chat(prompt)
    response_thread = record_stream(stream)

    # Verify files were created
    assert (tmp_path / 'project/file1.txt').read_text().strip() == 'content1'
    assert (tmp_path / 'project/file2.txt').read_text().strip() == 'content2'

    # Verify status messages
    # We expect status messages for operations and summaries.
    status_messages = [m for m in response_thread if m.intent == ChatIntent.STATUS]

    # Check for logs
    assert any("Written `~/project/file1.txt`" in m.content for m in status_messages)
    assert any("Written `~/project/file2.txt`" in m.content for m in status_messages)

    # Check for summaries (one for each response message execution)
    summaries = [m for m in status_messages if "tool calls executed" in m.content]
    assert len(summaries) == 2
    assert all("All 1 tool calls executed" in m.content for m in summaries)

def test_agent_autonomy_command_persistence(tmp_path: Path):
    """Tests that @autonomy command changes autonomy and persists it."""
    model = MockModel('echo')

    step = StepAutonomy()
    profiles = {'step': step}

    class AutonomyAwareAgent(Agent):
        def handle_setup(self, env):
            super().handle_setup(env)
            # Autonomy commands are handled by default in Agent.handle_commands

    agent = AutonomyAwareAgent(
        'agent',
        model,
        session_history=tmp_path,
        autonomy=NoAutonomy(),
        autonomy_profiles=profiles
    )

    # Turn 1: Switch to 'step' autonomy
    prompt1 = ChatThread([ChatMessage(ChatIntent.PROMPT, "@autonomy:step")])
    record_stream(agent.chat(prompt1))

    # Turn 2: Verify autonomy persists
    # We will check if it persists by checking the saved file in session history
    session_hash = _hash_thread(prompt1)
    autonomy_file = tmp_path / session_hash / 'autonomy.txt'
    assert autonomy_file.exists()
    assert autonomy_file.read_text().strip() == 'step'

    # Also verify by running a new turn and checking if autorun is enabled in environment?
    # Hard to check internal state directly without subclassing or mocking.
    # But persistence test covers the core requirement.

def test_project_command_summary(tmp_path: Path):
    """Tests that project selection command adds project summary to the context."""
    model = MockModel('echo')

    # Setup a project environment with a mock project
    from llobot.projects.marker import MarkerProject
    project = MarkerProject("myproject")
    from llobot.projects.library.predefined import PredefinedProjectLibrary
    library = PredefinedProjectLibrary({'myproject': project})

    # Agent base class doesn't handle project commands by default anymore.
    class ProjectAwareAgent(Agent):
        def handle_setup(self, env):
            super().handle_setup(env)
            from llobot.commands.project import handle_project_commands
            handle_project_commands(env)

    agent = ProjectAwareAgent('agent', model, session_history=tmp_path, projects=library)
    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "@myproject Hello")])
    record_stream(agent.chat(prompt))
    context = model.history[0]

    assert "Projects:" in context
    assert "- Marker `~/myproject`" in context

    # Verify that project summary is NOT included if projects didn't change (e.g. no @project command)
    model = MockModel('echo')
    agent = ProjectAwareAgent('agent', model, session_history=tmp_path, projects=library)
    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "Hello")])
    record_stream(agent.chat(prompt))
    context = model.history[0]

    assert "Projects:" not in context

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

def test_agent_exception_handling(tmp_path: Path):
    """Tests that Agent catches exceptions during command processing and reports them as status messages."""
    model = MockModel('echo')

    class BrokenAgent(Agent):
        def handle_commands(self, env):
            super().handle_commands(env)
            raise RuntimeError("Something went wrong!")

    agent = BrokenAgent('broken', model, session_history=tmp_path)
    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "Hello")])
    stream = agent.chat(prompt)
    response_thread = record_stream(stream)

    # Verify that the exception was caught and reported as a status message
    status_msg = next((m for m in response_thread if m.intent == ChatIntent.STATUS), None)
    assert status_msg
    assert "Error processing commands:" in status_msg.content
    assert "Something went wrong!" in status_msg.content

    # Verify that the prompt was swallowed (no response from model)
    response_msg = next((m for m in response_thread if m.intent == ChatIntent.RESPONSE), None)
    assert response_msg is None

def test_agent_unrecognized_command_error(tmp_path: Path):
    """Tests that unrecognized commands result in a status message instead of crashing."""
    model = MockModel('echo')
    agent = Agent('agent', model, session_history=tmp_path)

    # @invalid is not a registered command, so handle_unrecognized_commands should raise ValueError,
    # which should be caught by the try-except block.
    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "@invalid command")])
    stream = agent.chat(prompt)
    response_thread = record_stream(stream)

    status_msg = next((m for m in response_thread if m.intent == ChatIntent.STATUS), None)
    assert status_msg
    assert "Error processing commands:" in status_msg.content
    assert "Unrecognized: invalid" in status_msg.content

    # Verify that the prompt was swallowed (no response from model)
    response_msg = next((m for m in response_thread if m.intent == ChatIntent.RESPONSE), None)
    assert response_msg is None
