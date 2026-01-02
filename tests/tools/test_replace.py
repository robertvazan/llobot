from __future__ import annotations
from pathlib import PurePosixPath
import pytest
from llobot.environments import Environment
from llobot.environments.projects import ProjectEnv
from llobot.environments.tools import ToolEnv
from llobot.tools.replace import ReplaceTool, ReplaceToolCall, rust_to_python_replacement


class MockProject:
    def __init__(self):
        self.files = {}

    def read(self, path: PurePosixPath) -> str | None:
        return self.files.get(path)

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


# Tests for rust_to_python_replacement

def test_rust_to_python_numbered_groups():
    assert rust_to_python_replacement('$1') == '\\1'
    assert rust_to_python_replacement('$2') == '\\2'
    assert rust_to_python_replacement('$12') == '\\12'


def test_rust_to_python_entire_match():
    assert rust_to_python_replacement('$0') == '\\g<0>'


def test_rust_to_python_named_groups():
    assert rust_to_python_replacement('$name') == '\\g<name>'
    assert rust_to_python_replacement('${name}') == '\\g<name>'
    assert rust_to_python_replacement('$foo_bar') == '\\g<foo_bar>'
    assert rust_to_python_replacement('${foo_bar}') == '\\g<foo_bar>'


def test_rust_to_python_literal_dollar():
    assert rust_to_python_replacement('$$') == '$'
    assert rust_to_python_replacement('$$100') == '$100'


def test_rust_to_python_mixed():
    assert rust_to_python_replacement('prefix $1 middle $2 suffix') == 'prefix \\1 middle \\2 suffix'
    assert rust_to_python_replacement('$1-$2') == '\\1-\\2'
    assert rust_to_python_replacement('${name}: $1') == '\\g<name>: \\1'


def test_rust_to_python_no_replacement():
    assert rust_to_python_replacement('plain text') == 'plain text'
    assert rust_to_python_replacement('') == ''


def test_rust_to_python_lone_dollar():
    assert rust_to_python_replacement('$') == '$'
    assert rust_to_python_replacement('price: $') == 'price: $'


def test_rust_to_python_dollar_special_char():
    assert rust_to_python_replacement('$!') == '$!'
    assert rust_to_python_replacement('$.') == '$.'


def test_rust_to_python_empty_braced_name():
    with pytest.raises(ValueError, match="Empty group name"):
        rust_to_python_replacement('${}')


def test_rust_to_python_invalid_braced_name():
    with pytest.raises(ValueError, match="Invalid group name"):
        rust_to_python_replacement('${123}')
    with pytest.raises(ValueError, match="Invalid group name"):
        rust_to_python_replacement('${foo-bar}')


# Tests for ReplaceTool.matches_line

def test_replace_tool_matches(env):
    tool = ReplaceTool()
    assert tool.matches_line(env, 'sd foo bar ~/file.txt')
    assert tool.matches_line(env, 'sd "foo bar" baz ~/path/to/file.py')
    assert tool.matches_line(env, "sd 'pattern' 'replacement' ~/file")


def test_replace_tool_no_match(env):
    tool = ReplaceTool()
    assert not tool.matches_line(env, 'sed foo bar ~/file.txt')
    assert not tool.matches_line(env, 'sd foo ~/file.txt')
    assert not tool.matches_line(env, 'sd foo bar baz ~/file.txt')
    assert not tool.matches_line(env, 'sd')


# Tests for ReplaceTool.parse_line

def test_replace_tool_parse(env):
    tool = ReplaceTool()
    call = tool.parse_line(env, 'sd foo bar ~/path/to/file.txt')
    assert isinstance(call, ReplaceToolCall)
    assert call._path == PurePosixPath('path/to/file.txt')
    assert call._pattern == 'foo'
    assert call._replacement == 'bar'


def test_replace_tool_parse_quoted(env):
    tool = ReplaceTool()
    call = tool.parse_line(env, 'sd "foo bar" "baz qux" ~/file.txt')
    assert call._pattern == 'foo bar'
    assert call._replacement == 'baz qux'


# Tests for ReplaceToolCall.execute

def test_execute_simple_replace(env):
    project = env[ProjectEnv].union
    project.write(PurePosixPath('file.txt'), 'hello world\n')

    call = ReplaceToolCall(PurePosixPath('file.txt'), 'world', 'universe')
    call.execute(env)

    assert project.files[PurePosixPath('file.txt')] == 'hello universe\n'


def test_execute_regex_replace(env):
    project = env[ProjectEnv].union
    project.write(PurePosixPath('file.txt'), 'foo123bar\n')

    call = ReplaceToolCall(PurePosixPath('file.txt'), r'\d+', 'NUM')
    call.execute(env)

    assert project.files[PurePosixPath('file.txt')] == 'fooNUMbar\n'


def test_execute_capture_group(env):
    project = env[ProjectEnv].union
    project.write(PurePosixPath('file.txt'), 'hello world\n')

    call = ReplaceToolCall(PurePosixPath('file.txt'), r'(\w+) (\w+)', '$2 $1')
    call.execute(env)

    assert project.files[PurePosixPath('file.txt')] == 'world hello\n'


def test_execute_named_group(env):
    project = env[ProjectEnv].union
    project.write(PurePosixPath('file.txt'), 'name: John\n')

    call = ReplaceToolCall(PurePosixPath('file.txt'), r'name: (?P<n>\w+)', 'user: $n')
    call.execute(env)

    assert project.files[PurePosixPath('file.txt')] == 'user: John\n'


def test_execute_entire_match(env):
    project = env[ProjectEnv].union
    project.write(PurePosixPath('file.txt'), 'hello\n')

    call = ReplaceToolCall(PurePosixPath('file.txt'), r'hello', '[$0]')
    call.execute(env)

    assert project.files[PurePosixPath('file.txt')] == '[hello]\n'


def test_execute_multiple_occurrences(env):
    project = env[ProjectEnv].union
    project.write(PurePosixPath('file.txt'), 'foo bar foo baz foo\n')

    call = ReplaceToolCall(PurePosixPath('file.txt'), 'foo', 'qux')
    call.execute(env)

    assert project.files[PurePosixPath('file.txt')] == 'qux bar qux baz qux\n'


def test_execute_case_sensitive(env):
    """Ensures regex is case-sensitive by default."""
    project = env[ProjectEnv].union
    project.write(PurePosixPath('file.txt'), 'Hello HELLO hello\n')

    call = ReplaceToolCall(PurePosixPath('file.txt'), 'hello', 'hi')
    call.execute(env)

    assert project.files[PurePosixPath('file.txt')] == 'Hello HELLO hi\n'


def test_execute_pattern_not_found(env):
    project = env[ProjectEnv].union
    project.write(PurePosixPath('file.txt'), 'hello world\n')

    call = ReplaceToolCall(PurePosixPath('file.txt'), 'notfound', 'replacement')
    with pytest.raises(ValueError, match='Pattern not found'):
        call.execute(env)


def test_execute_file_not_found(env):
    call = ReplaceToolCall(PurePosixPath('nonexistent.txt'), 'foo', 'bar')
    with pytest.raises(ValueError, match='File not found'):
        call.execute(env)


def test_execute_invalid_regex(env):
    project = env[ProjectEnv].union
    project.write(PurePosixPath('file.txt'), 'content\n')

    call = ReplaceToolCall(PurePosixPath('file.txt'), '[invalid', 'replacement')
    with pytest.raises(ValueError, match='Invalid regex pattern'):
        call.execute(env)


def test_execute_literal_dollar(env):
    project = env[ProjectEnv].union
    project.write(PurePosixPath('file.txt'), 'price: 100\n')

    call = ReplaceToolCall(PurePosixPath('file.txt'), r'price: (\d+)', 'cost: $$$1')
    call.execute(env)

    assert project.files[PurePosixPath('file.txt')] == 'cost: $100\n'


def test_title():
    call = ReplaceToolCall(PurePosixPath('path/to/file.txt'), 'foo', 'bar')
    # shlex.join quotes paths with ~ since it's a shell special character
    assert call.title == "sd foo bar '~/path/to/file.txt'"


def test_title_with_spaces():
    call = ReplaceToolCall(PurePosixPath('file.txt'), 'foo bar', 'baz qux')
    assert call.title == "sd 'foo bar' 'baz qux' '~/file.txt'"
