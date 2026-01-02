from __future__ import annotations
import textwrap
from pathlib import Path
import pytest
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.thread import ChatThread
from llobot.commands.accept import handle_accept_command
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.projects import ProjectEnv
from llobot.environments.prompt import PromptEnv
from llobot.environments.status import StatusEnv
from llobot.environments.tools import ToolEnv
from llobot.projects.directory import DirectoryProject
from llobot.projects.library.predefined import PredefinedProjectLibrary
from llobot.tools.cat import CatTool
from llobot.tools.code import DummyCodeBlockTool
from llobot.tools.write import WriteTool
from llobot.tools.move import MoveTool
from llobot.tools.remove import RemoveTool
from llobot.tools.script import ScriptTool

TOOLS = [WriteTool(), MoveTool(), RemoveTool(), CatTool(), ScriptTool(), DummyCodeBlockTool()]

def test_accept_command_success(tmp_path: Path):
    # Setup project
    project_dir = tmp_path / "myproject"
    project_dir.mkdir(parents=True)
    (project_dir / "file1.txt").write_text("content1")
    (project_dir / "file3.txt").write_text("content3")

    # Setup environment
    env = Environment()
    project = DirectoryProject(project_dir, prefix="myproject", mutable=True)
    project_library = PredefinedProjectLibrary({"myproject": project})
    env[ProjectEnv].configure(project_library)
    env[ProjectEnv].add("myproject")
    for tool in TOOLS:
        env[ToolEnv].register(tool)

    # Setup prompt with a model response containing tool calls
    response_content = textwrap.dedent("""
        I will perform the requested file operations.

        <details>
        <summary>Write: ~/myproject/file2.txt</summary>

        ```
        new content
        ```

        </details>

        ```toolscript
        rm ~/myproject/file1.txt
        cat ~/myproject/file3.txt
        ```
    """)
    prompt = ChatThread([
        ChatMessage(ChatIntent.PROMPT, "do stuff"),
        ChatMessage(ChatIntent.RESPONSE, response_content),
        ChatMessage(ChatIntent.PROMPT, "@accept"),
    ])
    env[PromptEnv].set(prompt)

    # Execute command
    handled = handle_accept_command("accept", env)
    assert handled

    # Verify project state
    assert not (project_dir / "file1.txt").exists()
    assert (project_dir / "file2.txt").is_file()
    assert (project_dir / "file2.txt").read_text() == "new content\n"

    # Verify status messages
    status_env = env[StatusEnv]
    content = status_env.content()

    assert "Tool call log" in content

    # Check strict formatting and separation
    expected_log_fragment = (
        "Running tool: write ~/myproject/file2.txt\n"
        "Success.\n"
        "\n"
        "Running tool: rm ~/myproject/file1.txt\n"
        "Success.\n"
        "\n"
        "Running tool: cat ~/myproject/file3.txt"
    )
    assert expected_log_fragment in content

    # Output should NOT be in status
    assert "File: ~/myproject/file3.txt" not in content
    assert "content3" not in content
    assert "✅ All 3 tool calls executed." in content

    # Verify context messages
    context_env = env[ContextEnv]
    assert context_env.populated
    context_messages = context_env.build().messages
    assert len(context_messages) == 1
    assert context_messages[0].intent == ChatIntent.SYSTEM
    assert "File: ~/myproject/file3.txt" in context_messages[0].content
    assert "content3" in context_messages[0].content

def test_accept_command_failure(tmp_path: Path):
    # Setup project
    project_dir = tmp_path / "myproject"
    project_dir.mkdir(parents=True)

    # Setup environment
    env = Environment()
    project = DirectoryProject(project_dir, prefix="myproject", mutable=True)
    project_library = PredefinedProjectLibrary({"myproject": project})
    env[ProjectEnv].configure(project_library)
    env[ProjectEnv].add("myproject")
    for tool in TOOLS:
        env[ToolEnv].register(tool)

    # Setup prompt with a model response containing a failing tool call
    response_content = textwrap.dedent("""
        ```toolscript
        rm ~/myproject/nonexistent.txt
        ```
    """)
    prompt = ChatThread([
        ChatMessage(ChatIntent.PROMPT, "do stuff"),
        ChatMessage(ChatIntent.RESPONSE, response_content),
        ChatMessage(ChatIntent.PROMPT, "@accept"),
    ])
    env[PromptEnv].set(prompt)

    # Execute command
    handled = handle_accept_command("accept", env)
    assert handled

    # Verify status messages
    status_env = env[StatusEnv]
    content = status_env.content()
    assert "Running tool: rm ~/myproject/nonexistent.txt" in content
    assert "Error executing:" in content
    assert "Failed." in content
    assert "Error executing:" in content
    assert "❌ 0 of 1 tool calls executed." in content

def test_accept_command_no_tool_calls():
    # Setup environment
    env = Environment()
    for tool in TOOLS:
        env[ToolEnv].register(tool)

    # Setup prompt with a model response without tool calls
    response_content = "I'm not sure what to do."
    prompt = ChatThread([
        ChatMessage(ChatIntent.PROMPT, "do stuff"),
        ChatMessage(ChatIntent.RESPONSE, response_content),
        ChatMessage(ChatIntent.PROMPT, "@accept"),
    ])
    env[PromptEnv].set(prompt)

    with pytest.raises(ValueError, match="No tool calls to execute."):
        handle_accept_command("accept", env)

def test_accept_command_no_response():
    env = Environment()
    prompt = ChatThread([
        ChatMessage(ChatIntent.PROMPT, "do stuff"),
        ChatMessage(ChatIntent.PROMPT, "@accept"),
    ])
    env[PromptEnv].set(prompt)
    with pytest.raises(ValueError, match="Nothing to accept."):
        handle_accept_command("accept", env)

def test_accept_command_not_accept():
    env = Environment()
    assert not handle_accept_command("not-accept", env)
