from __future__ import annotations
from pathlib import PurePosixPath
import pytest
from llobot.chats.intent import ChatIntent
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.projects import ProjectEnv
from llobot.chats.message import ChatMessage
from llobot.tools.script.replace import ScriptReplace, rust_to_python_replacement


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


class MockContextEnv:
    def __init__(self):
        self.messages = []

    def add(self, message: ChatMessage):
        self.messages.append(message)

@pytest.fixture
def env():
    env = Environment()
    env._components[ProjectEnv] = MockProjectEnv()
    env._components[ContextEnv] = MockContextEnv()
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


# Tests for ScriptReplace.execute

def test_execute_simple_replace(env):
    project = env[ProjectEnv].union
    project.write(PurePosixPath('file.txt'), 'hello world\n')

    tool = ScriptReplace()
    assert tool.execute(env, "sd world universe ~/file.txt")

    assert project.files[PurePosixPath('file.txt')] == 'hello universe\n'

    # Check that status and listing messages were added
    messages = env[ContextEnv].messages
    assert len(messages) == 2
    assert messages[0].intent == ChatIntent.STATUS
    assert "Replaced 1 matches" in messages[0].content
    assert messages[1].intent == ChatIntent.SYSTEM
    assert "File: ~/file.txt" in messages[1].content
    assert "hello universe" in messages[1].content


def test_execute_regex_replace(env):
    project = env[ProjectEnv].union
    project.write(PurePosixPath('file.txt'), 'foo123bar\n')

    tool = ScriptReplace()
    # Backslashes inside quotes are preserved by shlex
    tool.execute(env, r"sd '\d+' NUM ~/file.txt")

    assert project.files[PurePosixPath('file.txt')] == 'fooNUMbar\n'


def test_execute_capture_group(env):
    project = env[ProjectEnv].union
    project.write(PurePosixPath('file.txt'), 'hello world\n')

    tool = ScriptReplace()
    # Need to quote arguments if they contain spaces
    tool.execute(env, r"sd '(\w+) (\w+)' '$2 $1' ~/file.txt")

    assert project.files[PurePosixPath('file.txt')] == 'world hello\n'


def test_execute_named_group(env):
    project = env[ProjectEnv].union
    project.write(PurePosixPath('file.txt'), 'name: John\n')

    tool = ScriptReplace()
    tool.execute(env, r"sd 'name: (?P<n>\w+)' 'user: $n' ~/file.txt")

    assert project.files[PurePosixPath('file.txt')] == 'user: John\n'


def test_execute_entire_match(env):
    project = env[ProjectEnv].union
    project.write(PurePosixPath('file.txt'), 'hello\n')

    tool = ScriptReplace()
    tool.execute(env, r"sd hello '[$0]' ~/file.txt")

    assert project.files[PurePosixPath('file.txt')] == '[hello]\n'


def test_execute_multiple_occurrences(env):
    project = env[ProjectEnv].union
    project.write(PurePosixPath('file.txt'), 'foo bar foo baz foo\n')

    tool = ScriptReplace()
    tool.execute(env, "sd foo qux ~/file.txt")

    assert project.files[PurePosixPath('file.txt')] == 'qux bar qux baz qux\n'


def test_execute_case_sensitive(env):
    """Ensures regex is case-sensitive by default."""
    project = env[ProjectEnv].union
    project.write(PurePosixPath('file.txt'), 'Hello HELLO hello\n')

    tool = ScriptReplace()
    tool.execute(env, "sd hello hi ~/file.txt")

    assert project.files[PurePosixPath('file.txt')] == 'Hello HELLO hi\n'


def test_execute_pattern_not_found(env):
    project = env[ProjectEnv].union
    project.write(PurePosixPath('file.txt'), 'hello world\n')

    tool = ScriptReplace()
    with pytest.raises(ValueError, match='Pattern not found'):
        tool.execute(env, "sd notfound replacement ~/file.txt")


def test_execute_file_not_found(env):
    tool = ScriptReplace()
    with pytest.raises(ValueError, match='File not found'):
        tool.execute(env, "sd foo bar ~/nonexistent.txt")


def test_execute_invalid_regex(env):
    project = env[ProjectEnv].union
    project.write(PurePosixPath('file.txt'), 'content\n')

    tool = ScriptReplace()
    with pytest.raises(ValueError, match='Invalid regex pattern'):
        tool.execute(env, "sd '[invalid' replacement ~/file.txt")


def test_execute_literal_dollar(env):
    project = env[ProjectEnv].union
    project.write(PurePosixPath('file.txt'), 'price: 100\n')

    tool = ScriptReplace()
    tool.execute(env, r"sd 'price: (\d+)' 'cost: $$$1' ~/file.txt")

    assert project.files[PurePosixPath('file.txt')] == 'cost: $100\n'
