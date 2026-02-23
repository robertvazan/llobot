from pathlib import PurePosixPath
from textwrap import dedent
import pytest
from llobot.chats.intent import ChatIntent
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.projects import ProjectEnv
from llobot.projects import Project
from llobot.projects.library import ProjectLibrary
from llobot.tools.shell import ShellTool
from llobot.tools.reader import ToolReader

class MockProject(Project):
    def __init__(self, prefixes: set[PurePosixPath], executable_paths: set[PurePosixPath]):
        self._prefixes = prefixes
        self._executable_paths = executable_paths
        self.executed_scripts = []

    @property
    def prefixes(self) -> set[PurePosixPath]:
        return self._prefixes

    def executable(self, path: PurePosixPath) -> bool:
        return path in self._executable_paths

    def execute(self, path: PurePosixPath, script: str) -> str:
        if not self.executable(path):
            raise PermissionError(f"Path is not allowed for execution: {path}")
        self.executed_scripts.append((path, script))
        return f"Output from {path}: {script.splitlines()[0]}"

class MockLibrary(ProjectLibrary):
    def __init__(self, project: Project):
        self.project = project

    def lookup(self, key: str) -> list[Project]:
        return [self.project]

@pytest.fixture
def env() -> Environment:
    return Environment()

def wrap_script(script: str, header: str = "desc @ ~/proj") -> str:
    return dedent(f"""
        <details>
        <summary>Shell: {header}</summary>

        ```sh
        {script}
        ```
        </details>
    """).strip()

def test_shell_tool_explicit_path(env: Environment):
    project = MockProject(
        {PurePosixPath('proj')},
        {PurePosixPath('proj')}
    )
    env[ProjectEnv].configure(MockLibrary(project))
    env[ProjectEnv].add('any')

    tool = ShellTool()
    script_content = "echo hello"
    source = wrap_script(script_content, "run echo @ ~/proj")

    reader = ToolReader(source)
    tool.execute(env, reader)
    assert reader.success_count == 1

    assert len(project.executed_scripts) == 1
    path, executed_script = project.executed_scripts[0]
    assert path == PurePosixPath('proj')
    assert "echo hello" in executed_script

    # Check context output
    context = env[ContextEnv].build()
    assert len(context) == 1
    msg = context[0]
    assert msg.intent == ChatIntent.SYSTEM
    assert "Shell output: run echo @ ~/proj" in msg.content
    assert "Output from proj" in msg.content

def test_shell_tool_fallback(env: Environment):
    project = MockProject(
        {PurePosixPath('proj')},
        {PurePosixPath('proj')}
    )
    env[ProjectEnv].configure(MockLibrary(project))
    env[ProjectEnv].add('any')

    tool = ShellTool()
    script_content = "echo hello"
    source = wrap_script(script_content, "run echo")

    reader = ToolReader(source)
    tool.execute(env, reader)
    assert reader.success_count == 1

    assert len(project.executed_scripts) == 1
    path, _ = project.executed_scripts[0]
    assert path == PurePosixPath('proj')

    # Verify context output includes the resolved path
    context = env[ContextEnv].build()
    assert len(context) == 1
    msg = context[0]
    assert "Shell output: run echo @ ~/proj" in msg.content

def test_shell_tool_ambiguous_fallback(env: Environment):
    project = MockProject(
        {PurePosixPath('p1'), PurePosixPath('p2')},
        {PurePosixPath('p1'), PurePosixPath('p2')}
    )
    env[ProjectEnv].configure(MockLibrary(project))
    env[ProjectEnv].add('any')

    tool = ShellTool()
    script_content = "echo hello"
    source = wrap_script(script_content, "run echo")

    reader = ToolReader(source)
    with pytest.raises(ValueError, match="multiple executable projects found"):
        tool.execute(env, reader)

    assert reader.position > 0 # Should have advanced
    assert reader.tool_count == 1

def test_shell_tool_no_executable_fallback(env: Environment):
    project = MockProject(
        {PurePosixPath('p1')},
        set()
    )
    env[ProjectEnv].configure(MockLibrary(project))
    env[ProjectEnv].add('any')

    tool = ShellTool()
    script_content = "echo hello"
    source = wrap_script(script_content, "run echo")

    reader = ToolReader(source)
    with pytest.raises(ValueError, match="no executable projects found"):
        tool.execute(env, reader)

def test_shell_tool_last_at_in_header(env: Environment):
    project = MockProject(
        {PurePosixPath('proj')},
        {PurePosixPath('proj')}
    )
    env[ProjectEnv].configure(MockLibrary(project))
    env[ProjectEnv].add('any')

    tool = ShellTool()
    # Description contains @ symbol
    source = wrap_script("echo hello", "run @ my place @ ~/proj")

    reader = ToolReader(source)
    tool.execute(env, reader)

    context = env[ContextEnv].build()
    msg = context[0]
    assert "Shell output: run @ my place @ ~/proj" in msg.content

def test_shell_tool_sanitizes_output(env: Environment):
    project = MockProject(
        {PurePosixPath('proj')},
        {PurePosixPath('proj')}
    )
    # Inject behavior to return control characters
    # MockProject returns the first line of the script as output

    env[ProjectEnv].configure(MockLibrary(project))
    env[ProjectEnv].add('any')

    tool = ShellTool()
    # \x1b will be in the script, so it will be in the output.
    source = wrap_script("echo \x1b[31mRed", "run color")

    tool.execute(env, ToolReader(source))

    context = env[ContextEnv].build()
    msg = context[0]

    # We expect the control characters to be escaped
    assert "\\x1b[31mRed" in msg.content
    # And ensure raw control characters are NOT present
    assert "\x1b" not in msg.content
