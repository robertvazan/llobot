from datetime import timedelta
from pathlib import Path
from textwrap import dedent
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.stream import record_stream
from llobot.chats.thread import ChatThread
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.roles.agent import Agent
from llobot.roles.autonomy import Autonomy, LimitedAutonomy, NoAutonomy, StepAutonomy
from llobot.tools.write import WriteTool
from llobot.projects.directory import DirectoryProject
from llobot.projects.library.predefined import PredefinedProjectLibrary
from tests.models.mock import MockModel

class ProjectAwareAgent(Agent):
    def handle_setup(self, env):
        super().handle_setup(env)
        from llobot.commands.project import handle_project_commands
        handle_project_commands(env)

def test_autonomy_autorun():
    assert not Autonomy().autorun
    assert not NoAutonomy().autorun
    assert StepAutonomy().autorun
    assert LimitedAutonomy().autorun

def test_autonomy_start():
    env = Environment()
    permit = Autonomy().start(env)
    assert not permit.valid(env)

    permit = NoAutonomy().start(env)
    assert not permit.valid(env)

    permit = StepAutonomy().start(env)
    assert not permit.valid(env)

def test_limited_autonomy_limits():
    autonomy = LimitedAutonomy(context=100, time=timedelta(seconds=1), turns=2)
    assert autonomy.context_limit == 100
    assert autonomy.time_limit == timedelta(seconds=1)
    assert autonomy.turn_limit == 2

def test_limited_autonomy_permit_turns():
    autonomy = LimitedAutonomy(turns=2)
    env = Environment()
    context = env[ContextEnv]

    permit = autonomy.start(env)
    assert permit.valid(env)

    # First turn
    context.add(ChatMessage(ChatIntent.RESPONSE, "First"))
    assert permit.valid(env)

    # Second turn
    context.add(ChatMessage(ChatIntent.RESPONSE, "Second"))
    # The limit is inclusive? No, the code says delta_turns >= limit.
    # Start turns = 0. Current turns = 2. Delta = 2. Limit = 2.
    # So it should be invalid now.
    assert not permit.valid(env)

    # Check status message
    assert len(context.builder) == 3
    assert context.builder[-1].intent == ChatIntent.STATUS
    assert "2 turns" in context.builder[-1].content

    # Check already notified logic
    assert not permit.valid(env)
    # Should not add another status message
    assert len(context.builder) == 3

def test_limited_autonomy_permit_context():
    autonomy = LimitedAutonomy(context=10)
    env = Environment()
    context = env[ContextEnv]
    # Start context is 0

    permit = autonomy.start(env)
    assert permit.valid(env)

    # "12345" has length 5. Overhead is 4. Total 9. Limit is 10.
    context.add(ChatMessage(ChatIntent.RESPONSE, "12345"))
    assert permit.valid(env)

    # "12" has length 2. Overhead is 4. Total 6. Cumulative 15. Limit 10.
    context.add(ChatMessage(ChatIntent.RESPONSE, "12"))
    assert not permit.valid(env)

    assert context.builder[-1].intent == ChatIntent.STATUS
    assert "10 chars" in context.builder[-1].content

def test_agent_autorun(tmp_path: Path):
    """Tests that Agent with StepAutonomy automatically executes tool calls."""
    # Setup project
    project = DirectoryProject(tmp_path / 'project', prefix="project", mutable=True)
    library = PredefinedProjectLibrary({'project': project})

    # Setup agent with autorun
    file_tool_call_str = dedent("""\
        <details>
        <summary>Write: ~/project/test.txt</summary>

        ```
        content
        ```

        </details>""")
    model = MockModel('mock', response=file_tool_call_str)

    # We need an agent that handles project commands to ensure environment is set up correctly for tools,
    # although here we are using absolute paths so maybe it's fine.
    # But wait, WriteTool writes to files.
    # The default Agent sets up ProjectEnv with the library.
    # However, to be safe, let's just ensure the project dir exists.
    (tmp_path / 'project').mkdir()

    agent = ProjectAwareAgent(
        'agent',
        model,
        tools=[WriteTool()],
        projects=library,
        autonomy=StepAutonomy(),
        session_history=tmp_path / 'sessions'
    )

    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "@project Do something")])
    stream = agent.chat(prompt)
    response_thread = record_stream(stream)

    # We expect:
    # 1. The response from the model (containing the tool call)
    # 2. Status messages from tool execution (Log + Summary)

    # Check response
    response = next((m for m in response_thread if m.intent == ChatIntent.RESPONSE), None)
    assert response
    assert "Write:" in response.content

    # Check status messages
    status_messages = [m for m in response_thread if m.intent == ChatIntent.STATUS]
    # Expect 2 status messages: one for log ("Written..."), one for summary ("✅ All 1 tool calls...")
    assert len(status_messages) == 2

    summary_msg = status_messages[-1]
    assert "✅ All 1 tool calls executed." in summary_msg.content

    # Check side effect
    assert (tmp_path / 'project/test.txt').read_text().strip() == 'content'

def test_agent_autorun_no_tools(tmp_path: Path):
    """Tests that autorun doesn't fail if no tools are detected in response."""
    model = MockModel('mock', response="Just a chat response.")
    agent = Agent(
        'agent',
        model,
        tools=[WriteTool()], # Tools are enabled
        autonomy=StepAutonomy(),
        session_history=tmp_path / 'sessions'
    )

    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "Chat")])
    stream = agent.chat(prompt)
    response_thread = record_stream(stream)

    # Should have response but no status messages (since no tools were called)
    response = next((m for m in response_thread if m.intent == ChatIntent.RESPONSE), None)
    assert response
    assert response.content == "Just a chat response."

    status_messages = [m for m in response_thread if m.intent == ChatIntent.STATUS]
    assert len(status_messages) == 0

def test_agent_no_autonomy(tmp_path: Path):
    """Tests that Agent without autonomy does NOT execute tool calls automatically."""
    # Setup project
    project = DirectoryProject(tmp_path / 'project', prefix="project", mutable=True)
    library = PredefinedProjectLibrary({'project': project})
    (tmp_path / 'project').mkdir()

    file_tool_call_str = dedent("""\
        <details>
        <summary>Write: ~/project/test.txt</summary>

        ```
        content
        ```

        </details>""")
    model = MockModel('mock', response=file_tool_call_str)

    agent = ProjectAwareAgent(
        'agent',
        model,
        tools=[WriteTool()],
        projects=library,
        autonomy=NoAutonomy(),
        session_history=tmp_path / 'sessions'
    )

    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "@project Do something")])
    stream = agent.chat(prompt)
    response_thread = record_stream(stream)

    # Expect response but NO status messages and NO side effects
    response = next((m for m in response_thread if m.intent == ChatIntent.RESPONSE), None)
    assert response

    status_messages = [m for m in response_thread if m.intent == ChatIntent.STATUS]
    assert len(status_messages) == 0

    assert not (tmp_path / 'project/test.txt').exists()

def test_agent_limited_autonomy_loop(tmp_path: Path):
    """Tests that LimitedAutonomy loops until invalid."""
    project = DirectoryProject(tmp_path / 'project', prefix="project", mutable=True)
    library = PredefinedProjectLibrary({'project': project})
    (tmp_path / 'project').mkdir()

    # Model that always responds with a tool call
    file_tool_call_str = dedent("""\
        <details>
        <summary>Write: ~/project/test.txt</summary>

        ```
        content
        ```

        </details>""")
    # It will loop.
    model = MockModel('mock', response=file_tool_call_str)

    # Limit to 3 turns
    autonomy = LimitedAutonomy(turns=3)

    agent = ProjectAwareAgent(
        'agent',
        model,
        tools=[WriteTool()],
        projects=library,
        autonomy=autonomy,
        session_history=tmp_path / 'sessions'
    )

    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "@project Loop")])
    stream = agent.chat(prompt)
    response_thread = record_stream(stream)

    # We expect 3 turns (3 responses + 3 executions) then a stop status.
    responses = [m for m in response_thread if m.intent == ChatIntent.RESPONSE]
    assert len(responses) == 3

    # Check for stop status
    status_messages = [m for m in response_thread if m.intent == ChatIntent.STATUS]
    stop_message = status_messages[-1]
    assert "Stopping to consult the user after 3 turns." in stop_message.content
