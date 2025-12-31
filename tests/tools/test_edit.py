from __future__ import annotations
from pathlib import PurePosixPath
import textwrap
import pytest
from llobot.environments import Environment
from llobot.environments.projects import ProjectEnv
from llobot.environments.tools import ToolEnv
from llobot.tools.edit import EditTool, EditToolCall

class MockProject:
    def __init__(self):
        self.files = {}

    def read(self, path: PurePosixPath) -> str:
        if path in self.files:
            return self.files[path]
        raise FileNotFoundError(path)

    def write(self, path: PurePosixPath, content: str):
        self.files[path] = content

class MockProjectEnv:
    def __init__(self):
        self.union = MockProject()

class MockToolEnv:
    def __init__(self):
        self.log_messages = []

    def log(self, message: str):
        self.log_messages.append(message)

@pytest.fixture
def env():
    env = Environment()
    env._components[ProjectEnv] = MockProjectEnv()
    env._components[ToolEnv] = MockToolEnv()
    return env

def test_parse_edit(env):
    source = textwrap.dedent("""
        <details>
        <summary>Edit: ~/file.txt</summary>

        ```text
        <<<<<<< SEARCH
        foo
        =======
        bar
        >>>>>>> REPLACE
        ```

        </details>
    """)
    tool = EditTool()
    calls = list(tool.parse(env, source.strip()))
    assert len(calls) == 1
    call = calls[0]
    assert isinstance(call, EditToolCall)
    assert call._path == PurePosixPath('file.txt')
    assert call._search.strip() == 'foo'
    assert call._replace.strip() == 'bar'

def test_parse_edit_empty_replace(env):
    source = textwrap.dedent("""
        <details>
        <summary>Edit: ~/file.txt</summary>

        ```text
        <<<<<<< SEARCH
        foo
        =======
        >>>>>>> REPLACE
        ```

        </details>
    """)
    tool = EditTool()
    calls = list(tool.parse(env, source.strip()))
    assert len(calls) == 1
    call = calls[0]
    assert isinstance(call, EditToolCall)
    assert call._replace.strip() == ''

def test_execute_edit(env):
    project = env[ProjectEnv].union
    project.write(PurePosixPath('file.txt'), "line1\nline2\nline3\n")

    call = EditToolCall(PurePosixPath('file.txt'), "line2", "replacement")
    call.execute(env)

    assert project.files[PurePosixPath('file.txt')] == "line1\nreplacement\nline3\n"

def test_execute_edit_not_found(env):
    project = env[ProjectEnv].union
    project.write(PurePosixPath('file.txt'), "line1\nline2\nline3\n")

    call = EditToolCall(PurePosixPath('file.txt'), "line4", "replacement")
    with pytest.raises(ValueError, match="Search block not found"):
        call.execute(env)

def test_execute_edit_ambiguous(env):
    project = env[ProjectEnv].union
    project.write(PurePosixPath('file.txt'), "line1\nline1\n")

    call = EditToolCall(PurePosixPath('file.txt'), "line1", "replacement")
    with pytest.raises(ValueError, match="Context is ambiguous"):
        call.execute(env)

def test_execute_edit_multi_line_ambiguous(env):
    project = env[ProjectEnv].union
    project.write(PurePosixPath('file.txt'), "line1\nline2\nline1\nline2\n")

    call = EditToolCall(PurePosixPath('file.txt'), "line1\nline2", "replacement")
    with pytest.raises(ValueError, match="Context is ambiguous"):
        call.execute(env)

def test_execute_edit_empty_search(env):
    project = env[ProjectEnv].union
    project.write(PurePosixPath('file.txt'), "content\n")

    call = EditToolCall(PurePosixPath('file.txt'), "", "replacement")
    with pytest.raises(ValueError, match="Search block cannot be empty"):
        call.execute(env)

def test_execute_edit_partial_match_ignored(env):
    """Ensures that matches strictly follow line boundaries."""
    project = env[ProjectEnv].union
    project.write(PurePosixPath('file.txt'), "foobar\n")

    call = EditToolCall(PurePosixPath('file.txt'), "bar", "baz")
    with pytest.raises(ValueError, match="Search block not found"):
        call.execute(env)

    assert project.files[PurePosixPath('file.txt')] == "foobar\n"

def test_execute_edit_start_match(env):
    """Ensures match works at the very beginning of the file."""
    project = env[ProjectEnv].union
    project.write(PurePosixPath('file.txt'), "foo\nbar\n")

    call = EditToolCall(PurePosixPath('file.txt'), "foo", "baz")
    call.execute(env)

    assert project.files[PurePosixPath('file.txt')] == "baz\nbar\n"

def test_execute_edit_middle_match(env):
    """Ensures match works in the middle of the file."""
    project = env[ProjectEnv].union
    project.write(PurePosixPath('file.txt'), "top\nmiddle\nbottom\n")

    call = EditToolCall(PurePosixPath('file.txt'), "middle", "center")
    call.execute(env)

    assert project.files[PurePosixPath('file.txt')] == "top\ncenter\nbottom\n"

def test_execute_edit_multi_line_match(env):
    """Ensures matching multiple lines works correctly."""
    project = env[ProjectEnv].union
    project.write(PurePosixPath('file.txt'), "line1\nline2\nline3\n")

    call = EditToolCall(PurePosixPath('file.txt'), "line2\nline3", "replacement")
    call.execute(env)

    assert project.files[PurePosixPath('file.txt')] == "line1\nreplacement\n"

def test_execute_edit_normalize_output(env):
    """Ensures output is normalized on write."""
    project = env[ProjectEnv].union
    project.write(PurePosixPath('file.txt'), "line1\nline2\n")

    # Replacement lacks newline
    call = EditToolCall(PurePosixPath('file.txt'), "line2", "replacement")
    call.execute(env)

    # Result should have newline
    assert project.files[PurePosixPath('file.txt')] == "line1\nreplacement\n"
