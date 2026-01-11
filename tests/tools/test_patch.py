from pathlib import PurePosixPath
from textwrap import dedent
import pytest
from llobot.chats.intent import ChatIntent
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.projects import ProjectEnv
from llobot.projects.directory import DirectoryProject
from llobot.formats.documents import standard_document_format
from llobot.tools.patch import PatchTool, PatchToolCall

@pytest.fixture
def env(tmp_path):
    project = DirectoryProject(tmp_path, prefix='test', mutable=True)
    env = Environment()
    env[ProjectEnv]._projects.add(project)
    return env

def test_slice_valid(env):
    tool = PatchTool()
    source = dedent("""
        <details>
        <summary>Patch: ~/test/file.txt</summary>

        ```diff
        @@
        -old
        +new
        ```

        </details>
    """).strip()
    assert tool.slice(env, source, 0) == len(source)

def test_parse_valid(env):
    tool = PatchTool()
    source = dedent("""
        <details>
        <summary>Patch: ~/test/file.txt</summary>

        ```diff
        @@
        -old
        +new
        ```

        </details>
    """).strip()
    calls = list(tool.parse(env, source))
    assert len(calls) == 1
    call = calls[0]
    assert isinstance(call, PatchToolCall)
    assert call._path == '~/test/file.txt'
    assert "old" in call._diff
    assert "new" in call._diff

def test_execute_simple_replacement(env, tmp_path):
    (tmp_path / 'file.txt').write_text("line1\nline2\nline3\n", encoding='utf-8')

    diff = dedent("""
        @@
        -line2
        +modified
    """)
    call = PatchToolCall('~/test/file.txt', diff, standard_document_format())
    call.execute(env)

    assert (tmp_path / 'file.txt').read_text(encoding='utf-8') == "line1\nmodified\nline3\n"

    context_env = env[ContextEnv]
    context_messages = context_env.build().messages
    log = "\n".join(m.content for m in context_messages if m.intent == ChatIntent.STATUS)
    output = "\n".join(m.content for m in context_messages if m.intent == ChatIntent.SYSTEM)

    assert "Applied 1 hunks to `~/test/file.txt`." in log
    assert "File: ~/test/file.txt" in output
    assert "modified" in output

def test_execute_with_context(env, tmp_path):
    (tmp_path / 'file.txt').write_text("A\nB\nC\nD\n", encoding='utf-8')

    diff = dedent("""
        @@
         A
        -B
        +MODIFIED
         C
    """)
    call = PatchToolCall('~/test/file.txt', diff, standard_document_format())
    call.execute(env)

    assert (tmp_path / 'file.txt').read_text(encoding='utf-8') == "A\nMODIFIED\nC\nD\n"

def test_execute_multiple_hunks(env, tmp_path):
    (tmp_path / 'file.txt').write_text("A\nB\nC\nD\nE\n", encoding='utf-8')

    diff = dedent("""
        @@
        -A
        +Start
        @@
         D
        -E
        +End
    """)
    call = PatchToolCall('~/test/file.txt', diff, standard_document_format())
    call.execute(env)

    assert (tmp_path / 'file.txt').read_text(encoding='utf-8') == "Start\nB\nC\nD\nEnd\n"

    context_env = env[ContextEnv]
    context_messages = context_env.build().messages
    log = "\n".join(m.content for m in context_messages if m.intent == ChatIntent.STATUS)

    assert "Applied 2 hunks to `~/test/file.txt`." in log

def test_execute_fail_not_found(env, tmp_path):
    (tmp_path / 'file.txt').write_text("A\nB\nC\n", encoding='utf-8')

    diff = dedent("""
        @@
        -D
        +E
    """)
    call = PatchToolCall('~/test/file.txt', diff, standard_document_format())
    with pytest.raises(ValueError, match="Hunk 1 failed. Search block not found"):
        call.execute(env)

def test_execute_fail_ambiguous(env, tmp_path):
    (tmp_path / 'file.txt').write_text("A\nA\nA\n", encoding='utf-8')

    diff = dedent("""
        @@
        -A
        +B
    """)
    call = PatchToolCall('~/test/file.txt', diff, standard_document_format())
    with pytest.raises(ValueError, match="Context is ambiguous"):
        call.execute(env)

def test_execute_fail_empty_search(env, tmp_path):
    (tmp_path / 'file.txt').write_text("A\n", encoding='utf-8')

    diff = dedent("""
        @@
        +New
    """)
    call = PatchToolCall('~/test/file.txt', diff, standard_document_format())
    with pytest.raises(ValueError, match="Hunk 1 search block is empty"):
        call.execute(env)

def test_execute_whole_line_enforcement(env, tmp_path):
    # 'target\n' exists in the content, but not at the start of a line
    (tmp_path / 'file.txt').write_text("prefix_target\n", encoding='utf-8')

    diff = dedent("""
        @@
        -target
        +replacement
    """)
    call = PatchToolCall('~/test/file.txt', diff, standard_document_format())

    with pytest.raises(ValueError, match="Search block not found"):
        call.execute(env)

def test_execute_ignore_header(env, tmp_path):
    (tmp_path / 'file.txt').write_text("A\n", encoding='utf-8')

    diff = dedent("""
        --- a/file.txt
        +++ b/file.txt
        @@
        -A
        +B
    """)
    call = PatchToolCall('~/test/file.txt', diff, standard_document_format())
    call.execute(env)
    assert (tmp_path / 'file.txt').read_text(encoding='utf-8') == "B\n"

def test_execute_normalization(env, tmp_path):
    (tmp_path / 'file.txt').write_text("A\nB\n", encoding='utf-8')

    # Input has irregular whitespace
    diff = dedent("""
        @@
        -B
        +C
    """)
    call = PatchToolCall('~/test/file.txt', diff, standard_document_format())
    call.execute(env)
    # Result should be normalized (no trailing empty lines beyond the terminal newline)
    assert (tmp_path / 'file.txt').read_text(encoding='utf-8') == "A\nC\n"

def test_execute_missing_file(env):
    call = PatchToolCall('~/test/missing.txt', "@@\n-a\n+b", standard_document_format())
    with pytest.raises(FileNotFoundError, match="File not found"):
        call.execute(env)

def test_atomic_execution(env, tmp_path):
    """Ensures file is not modified if any hunk fails."""
    (tmp_path / 'file.txt').write_text("A\nB\nC\n", encoding='utf-8')

    # First hunk matches, second hunk fails
    diff = dedent("""
        @@
        -A
        +ModifiedA
        @@
        -X
        +ModifiedX
    """)
    call = PatchToolCall('~/test/file.txt', diff, standard_document_format())
    with pytest.raises(ValueError, match="Search block not found"):
        call.execute(env)

    # File should be unchanged
    assert (tmp_path / 'file.txt').read_text(encoding='utf-8') == "A\nB\nC\n"

def test_strict_context_parsing(env, tmp_path):
    """Ensures context lines must start with space, not be empty."""
    (tmp_path / 'file.txt').write_text("A\n\nB\n", encoding='utf-8')

    # This diff has an empty line which should be rejected
    diff = dedent("""
        @@
        -A

        -B
        +C
    """)
    call = PatchToolCall('~/test/file.txt', diff, standard_document_format())
    # The empty line will fall through to the invalid line check
    with pytest.raises(ValueError, match="Invalid diff line"):
        call.execute(env)

def test_execute_ignore_trailing_whitespace_in_diff(env, tmp_path):
    (tmp_path / 'file.txt').write_text("line1\n", encoding='utf-8')

    # Diff has trailing whitespace on the context line
    diff = dedent("""
        @@
        -line1
        +line2
    """)
    call = PatchToolCall('~/test/file.txt', diff, standard_document_format())
    call.execute(env)

    assert (tmp_path / 'file.txt').read_text(encoding='utf-8') == "line2\n"

def test_execute_preserve_empty_lines_after_strip(env, tmp_path):
    (tmp_path / 'file.txt').write_text("A\n\nB\n", encoding='utf-8')

    # Diff uses context/delete lines that are effectively empty but have trailing spaces
    # Note: Using manual string construction to ensure trailing spaces are present
    diff = "@@\n A \n  \n-B \n+C\n"

    call = PatchToolCall('~/test/file.txt', diff, standard_document_format())
    call.execute(env)

    assert (tmp_path / 'file.txt').read_text(encoding='utf-8') == "A\n\nC\n"
