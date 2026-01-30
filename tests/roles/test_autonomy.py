from pathlib import Path
from textwrap import dedent
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.stream import record_stream
from llobot.chats.thread import ChatThread
from llobot.roles.agent import Agent
from llobot.roles.autonomy import HopAutonomy
from llobot.tools.write import WriteTool
from llobot.projects.directory import DirectoryProject
from llobot.projects.library.predefined import PredefinedProjectLibrary
from tests.models.mock import MockModel

class ProjectAwareAgent(Agent):
    def handle_setup(self, env):
        super().handle_setup(env)
        from llobot.commands.project import handle_project_commands
        handle_project_commands(env)

def test_agent_autorun(tmp_path: Path):
    """Tests that Agent with HopAutonomy automatically executes tool calls."""
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
        autonomy=HopAutonomy(),
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
        autonomy=HopAutonomy(),
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
        # Default is NoAutonomy
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
