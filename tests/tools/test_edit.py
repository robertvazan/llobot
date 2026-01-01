from __future__ import annotations
from pathlib import PurePosixPath
import textwrap
import pytest
from llobot.environments import Environment
from llobot.environments.projects import ProjectEnv
from llobot.environments.tools import ToolEnv
from llobot.projects.directory import DirectoryProject
from llobot.tools.edit import EditTool, EditToolCall

@pytest.fixture
def env(tmp_path):
    project = DirectoryProject(tmp_path, prefix='test', mutable=True)
    env = Environment()
    env[ProjectEnv]._projects.add(project)
    return env

def test_parse_edit(env):
    source = textwrap.dedent("""
        <details>
        <summary>Edit: ~/test/file.txt</summary>

        ```text
        foo
        @@@
        bar
        ```

        </details>
    """)
    tool = EditTool()
    calls = list(tool.parse(env, source.strip()))
    assert len(calls) == 1
    call = calls[0]
    assert isinstance(call, EditToolCall)
    assert call._path == PurePosixPath('test/file.txt')
    assert call._search.strip() == 'foo'
    assert call._replace.strip() == 'bar'

def test_parse_edit_empty_replace(env):
    source = textwrap.dedent("""
        <details>
        <summary>Edit: ~/test/file.txt</summary>

        ```text
        foo
        @@@
        ```

        </details>
    """)
    tool = EditTool()
    calls = list(tool.parse(env, source.strip()))
    assert len(calls) == 1
    call = calls[0]
    assert isinstance(call, EditToolCall)
    assert call._replace.strip() == ''

def test_parse_edit_content_with_at_signs(env):
    source = textwrap.dedent("""
        <details>
        <summary>Edit: ~/test/file.txt</summary>

        ```text
        foo
        @@@
        bar
        @@@@
        baz
        @@@
        qux
        ```

        </details>
    """)
    tool = EditTool()
    calls = list(tool.parse(env, source.strip()))
    assert len(calls) == 1
    call = calls[0]
    # @@@@ is the separator because it's longest
    assert call._search.strip() == "foo\n@@@\nbar"
    assert call._replace.strip() == "baz\n@@@\nqux"

def test_parse_edit_ambiguous_separator(env):
    source = textwrap.dedent("""
        <details>
        <summary>Edit: ~/test/file.txt</summary>

        ```text
        foo
        @@@
        bar
        @@@
        baz
        ```

        </details>
    """)
    tool = EditTool()
    with pytest.raises(ValueError, match="Ambiguous separator"):
        list(tool.parse(env, source.strip()))

def test_execute_edit(env, tmp_path):
    (tmp_path / 'file.txt').write_text("line1\nline2\nline3\n", encoding='utf-8')

    call = EditToolCall(PurePosixPath('test/file.txt'), "line2", "replacement")
    call.execute(env)

    assert (tmp_path / 'file.txt').read_text(encoding='utf-8') == "line1\nreplacement\nline3\n"

def test_execute_edit_not_found(env, tmp_path):
    (tmp_path / 'file.txt').write_text("line1\nline2\nline3\n", encoding='utf-8')

    call = EditToolCall(PurePosixPath('test/file.txt'), "line4", "replacement")
    with pytest.raises(ValueError, match="Search block not found"):
        call.execute(env)

def test_execute_edit_ambiguous(env, tmp_path):
    (tmp_path / 'file.txt').write_text("line1\nline1\n", encoding='utf-8')

    call = EditToolCall(PurePosixPath('test/file.txt'), "line1", "replacement")
    with pytest.raises(ValueError, match="Context is ambiguous"):
        call.execute(env)

def test_execute_edit_multi_line_ambiguous(env, tmp_path):
    (tmp_path / 'file.txt').write_text("line1\nline2\nline1\nline2\n", encoding='utf-8')

    call = EditToolCall(PurePosixPath('test/file.txt'), "line1\nline2", "replacement")
    with pytest.raises(ValueError, match="Context is ambiguous"):
        call.execute(env)

def test_execute_edit_empty_search(env, tmp_path):
    (tmp_path / 'file.txt').write_text("content\n", encoding='utf-8')

    call = EditToolCall(PurePosixPath('test/file.txt'), "", "replacement")
    with pytest.raises(ValueError, match="Search block cannot be empty"):
        call.execute(env)

def test_execute_edit_partial_match_ignored(env, tmp_path):
    """Ensures that matches strictly follow line boundaries."""
    (tmp_path / 'file.txt').write_text("foobar\n", encoding='utf-8')

    call = EditToolCall(PurePosixPath('test/file.txt'), "bar", "baz")
    with pytest.raises(ValueError, match="Search block not found"):
        call.execute(env)

    assert (tmp_path / 'file.txt').read_text(encoding='utf-8') == "foobar\n"

def test_execute_edit_start_match(env, tmp_path):
    """Ensures match works at the very beginning of the file."""
    (tmp_path / 'file.txt').write_text("foo\nbar\n", encoding='utf-8')

    call = EditToolCall(PurePosixPath('test/file.txt'), "foo", "baz")
    call.execute(env)

    assert (tmp_path / 'file.txt').read_text(encoding='utf-8') == "baz\nbar\n"

def test_execute_edit_middle_match(env, tmp_path):
    """Ensures match works in the middle of the file."""
    (tmp_path / 'file.txt').write_text("top\nmiddle\nbottom\n", encoding='utf-8')

    call = EditToolCall(PurePosixPath('test/file.txt'), "middle", "center")
    call.execute(env)

    assert (tmp_path / 'file.txt').read_text(encoding='utf-8') == "top\ncenter\nbottom\n"

def test_execute_edit_multi_line_match(env, tmp_path):
    """Ensures matching multiple lines works correctly."""
    (tmp_path / 'file.txt').write_text("line1\nline2\nline3\n", encoding='utf-8')

    call = EditToolCall(PurePosixPath('test/file.txt'), "line2\nline3", "replacement")
    call.execute(env)

    assert (tmp_path / 'file.txt').read_text(encoding='utf-8') == "line1\nreplacement\n"

def test_execute_edit_normalize_output(env, tmp_path):
    """Ensures output is normalized on write."""
    (tmp_path / 'file.txt').write_text("line1\nline2\n", encoding='utf-8')

    # Replacement lacks newline
    call = EditToolCall(PurePosixPath('test/file.txt'), "line2", "replacement")
    call.execute(env)

    # Result should have newline
    assert (tmp_path / 'file.txt').read_text(encoding='utf-8') == "line1\nreplacement\n"

def test_execute_edit_missing_file(env):
    """Ensures meaningful error when file is missing."""
    call = EditToolCall(PurePosixPath('test/missing.txt'), "foo", "bar")
    with pytest.raises(FileNotFoundError, match="File not found"):
        call.execute(env)

def test_parse_edit_with_shorter_fence(env):
    source = textwrap.dedent("""
        <details>
        <summary>Edit: ~/test/file.txt</summary>

        ````text
        ```
        shorter fence
        ```
        @@@
        bar
        ````

        </details>
    """)
    tool = EditTool()
    calls = list(tool.parse(env, source.strip()))
    assert len(calls) == 1
    call = calls[0]
    # Verify the inner backticks are preserved
    assert "```\nshorter fence\n```" in call._search

def test_parse_edit_with_indented_fence(env):
    source = textwrap.dedent("""
        <details>
        <summary>Edit: ~/test/file.txt</summary>

        ```text
         ```
         indented
         ```
        @@@
        bar
        ```

        </details>
    """)
    tool = EditTool()
    calls = list(tool.parse(env, source.strip()))
    assert len(calls) == 1

def test_parse_edit_with_conflicting_fence(env):
    source = textwrap.dedent("""
        <details>
        <summary>Edit: ~/test/file.txt</summary>

        ```text
        ```
        conflict
        ```
        @@@
        bar
        ```

        </details>
    """)
    tool = EditTool()
    with pytest.raises(ValueError, match="Content contains a line starting with"):
        list(tool.parse(env, source.strip()))

def test_parse_edit_with_midline_separator(env):
    source = textwrap.dedent("""
        <details>
        <summary>Edit: ~/test/file.txt</summary>

        ```text
        some text @@@ mid line
        @@@@
        other text @@@ mid line
        ```

        </details>
    """)
    tool = EditTool()
    calls = list(tool.parse(env, source.strip()))
    assert len(calls) == 1
    call = calls[0]
    # @@@@ is separator
    assert "some text @@@ mid line" in call._search
    assert "other text @@@ mid line" in call._replace
