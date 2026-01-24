from __future__ import annotations
import textwrap
from pathlib import Path
import pytest
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.thread import ChatThread
from llobot.commands.run import handle_run_command
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.projects import ProjectEnv
from llobot.environments.prompt import PromptEnv
from llobot.environments.tools import ToolEnv
from llobot.projects.directory import DirectoryProject
from llobot.projects.library.predefined import PredefinedProjectLibrary
from llobot.tools.dummy.code import DummyCodeBlockTool
from llobot.tools.read import ReadTool
from llobot.tools.write import WriteTool
from llobot.tools.script import ScriptTool, standard_script_tools

TOOLS = [WriteTool(), ReadTool(), ScriptTool(), *standard_script_tools(), DummyCodeBlockTool()]

def test_run_command_success(tmp_path: Path):
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

        ```text
        new content
        ```

        </details>

        <details>
        <summary>Script: cleanup</summary>

        ```sh
        rm ~/myproject/file1.txt
        ```

        </details>

        <details>
        <summary>Read: check result</summary>

        ```
        ~/myproject/file3.txt
        ```

        </details>
    """)
    prompt = ChatThread([
        ChatMessage(ChatIntent.PROMPT, "do stuff"),
        ChatMessage(ChatIntent.RESPONSE, response_content),
        ChatMessage(ChatIntent.PROMPT, "@run"),
    ])
    env[PromptEnv].set(prompt)

    # Execute command
    handled = handle_run_command("run", env)
    assert handled

    # Verify project state
    assert not (project_dir / "file1.txt").exists()
    assert (project_dir / "file2.txt").is_file()
    assert (project_dir / "file2.txt").read_text() == "new content\n"

    assert env[PromptEnv].swallowed

    # Verify context messages
    context_env = env[ContextEnv]
    assert context_env.populated
    context_messages = context_env.build().messages
    assert len(context_messages) == 4
    assert context_messages[0].intent == ChatIntent.STATUS
    assert "Written `~/myproject/file2.txt`" in context_messages[0].content

    assert context_messages[1].intent == ChatIntent.STATUS
    assert "Removed `~/myproject/file1.txt`" in context_messages[1].content

    assert context_messages[2].intent == ChatIntent.SYSTEM
    assert "File: ~/myproject/file3.txt" in context_messages[2].content

    assert context_messages[3].intent == ChatIntent.STATUS
    assert "✅ All 3 tool calls executed." in context_messages[3].content

def test_run_command_failure(tmp_path: Path):
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
        <details>
        <summary>Script: fail</summary>

        ```sh
        rm ~/myproject/nonexistent.txt
        ```

        </details>
    """)
    prompt = ChatThread([
        ChatMessage(ChatIntent.PROMPT, "do stuff"),
        ChatMessage(ChatIntent.RESPONSE, response_content),
        ChatMessage(ChatIntent.PROMPT, "@run"),
    ])
    env[PromptEnv].set(prompt)

    # Execute command
    handled = handle_run_command("run", env)
    assert handled
    assert env[PromptEnv].swallowed

    # Verify context messages
    context_env = env[ContextEnv]
    context_messages = context_env.build().messages
    assert len(context_messages) == 2

    content = context_messages[0].content
    assert "Error executing tool" in content
    assert "No such file or directory" in content

    assert "❌ 0 of 1 tool calls executed." in context_messages[1].content

def test_run_command_no_tool_calls():
    # Setup environment
    env = Environment()
    for tool in TOOLS:
        env[ToolEnv].register(tool)

    # Setup prompt with a model response without tool calls
    response_content = "I'm not sure what to do."
    prompt = ChatThread([
        ChatMessage(ChatIntent.PROMPT, "do stuff"),
        ChatMessage(ChatIntent.RESPONSE, response_content),
        ChatMessage(ChatIntent.PROMPT, "@run"),
    ])
    env[PromptEnv].set(prompt)

    with pytest.raises(ValueError, match="No tool calls to execute."):
        handle_run_command("run", env)

def test_run_command_no_response():
    env = Environment()
    prompt = ChatThread([
        ChatMessage(ChatIntent.PROMPT, "do stuff"),
        ChatMessage(ChatIntent.PROMPT, "@run"),
    ])
    env[PromptEnv].set(prompt)
    with pytest.raises(ValueError, match=r"Nothing to run \(no previous response found\)\."):
        handle_run_command("run", env)

def test_run_command_not_run():
    env = Environment()
    assert not handle_run_command("not-run", env)
