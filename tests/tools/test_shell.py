from pathlib import PurePosixPath
from textwrap import dedent
import pytest
from llobot.chats.intent import ChatIntent
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.projects import ProjectEnv
from llobot.projects import Project
from llobot.projects.library import ProjectLibrary
from llobot.tools.shell import ShellTool, ShellToolCall

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

def wrap_script(script: str) -> str:
    return f"```shelltool\n{script}\n```"

def test_shell_tool_explicit_cd(env: Environment):
    project = MockProject(
        {PurePosixPath('proj')},
        {PurePosixPath('proj')}
    )
    env[ProjectEnv].configure(MockLibrary(project))
    env[ProjectEnv].add('any')

    tool = ShellTool()
    script_content = dedent("""
        # comment
        cd ~/proj
        echo hello
    """).strip()
    source = wrap_script(script_content)

    calls = list(tool.parse(env, source))
    assert len(calls) == 1
    call = calls[0]
    assert isinstance(call, ShellToolCall)

    call.execute(env)

    assert len(project.executed_scripts) == 1
    path, executed_script = project.executed_scripts[0]
    assert path == PurePosixPath('proj')
    assert executed_script == script_content

    # Check context output
    context = env[ContextEnv].build()
    assert len(context) == 1
    msg = context[0]
    assert msg.intent == ChatIntent.STATUS
    assert "Shell tool output" in msg.content
    assert "```\n" in msg.content
    assert "Output from proj" in msg.content
    assert "# comment" in msg.content

def test_shell_tool_quoted_cd_with_extras(env: Environment):
    project = MockProject(
        {PurePosixPath('proj')},
        {PurePosixPath('proj')}
    )
    env[ProjectEnv].configure(MockLibrary(project))
    env[ProjectEnv].add('any')

    tool = ShellTool()
    # cd command with quotes, chaining, and inline comment
    script_content = dedent("""
        cd "~/proj" && echo hello # inline comment
    """).strip()
    source = wrap_script(script_content)

    calls = list(tool.parse(env, source))
    assert len(calls) == 1
    call = calls[0]

    call.execute(env)

    assert len(project.executed_scripts) == 1
    path, executed_script = project.executed_scripts[0]
    assert path == PurePosixPath('proj')
    assert executed_script == script_content

def test_shell_tool_fallback(env: Environment):
    project = MockProject(
        {PurePosixPath('proj')},
        {PurePosixPath('proj')}
    )
    env[ProjectEnv].configure(MockLibrary(project))
    env[ProjectEnv].add('any')

    tool = ShellTool()
    script_content = "echo hello"
    source = wrap_script(script_content)

    calls = list(tool.parse(env, source))
    call = calls[0]
    call.execute(env)

    assert len(project.executed_scripts) == 1
    path, _ = project.executed_scripts[0]
    assert path == PurePosixPath('proj')

def test_shell_tool_ambiguous_fallback(env: Environment):
    project = MockProject(
        {PurePosixPath('p1'), PurePosixPath('p2')},
        {PurePosixPath('p1'), PurePosixPath('p2')}
    )
    env[ProjectEnv].configure(MockLibrary(project))
    env[ProjectEnv].add('any')

    tool = ShellTool()
    script_content = "echo hello"
    source = wrap_script(script_content)

    calls = list(tool.parse(env, source))
    call = calls[0]

    with pytest.raises(ValueError, match="multiple executable projects found"):
        call.execute(env)

def test_shell_tool_no_executable_fallback(env: Environment):
    project = MockProject(
        {PurePosixPath('p1')},
        set()
    )
    env[ProjectEnv].configure(MockLibrary(project))
    env[ProjectEnv].add('any')

    tool = ShellTool()
    script_content = "echo hello"
    source = wrap_script(script_content)

    calls = list(tool.parse(env, source))
    call = calls[0]

    with pytest.raises(ValueError, match="no executable projects found"):
        call.execute(env)

def test_shell_tool_invalid_cd(env: Environment):
    project = MockProject(
        {PurePosixPath('proj')},
        {PurePosixPath('proj')}
    )
    env[ProjectEnv].configure(MockLibrary(project))
    env[ProjectEnv].add('any')

    tool = ShellTool()
    script_content = "cd /absolute/path"
    source = wrap_script(script_content)

    calls = list(tool.parse(env, source))
    call = calls[0]

    # It parses successfully, but execution fails because cd is not ~/
    with pytest.raises(ValueError, match="Shell script must start with 'cd ~/path'"):
        call.execute(env)
