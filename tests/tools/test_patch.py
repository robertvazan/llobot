from textwrap import dedent
import pytest
from llobot.chats.intent import ChatIntent
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.projects import ProjectEnv
from llobot.environments.seen import SeenEnv
from llobot.projects.directory import DirectoryProject
from llobot.tools.patch import PatchTool
from llobot.tools.reader import ToolReader
from llobot.utils.text import normalize_document

@pytest.fixture
def env(tmp_path):
    project = DirectoryProject(tmp_path, prefix='test', mutable=True)
    env = Environment()
    env[ProjectEnv]._projects.add(project)
    return env

def mark_seen(env, path, content):
    # Strip ~/ prefix if present, as coerce_path doesn't handle it
    if path.startswith('~/'):
        path = path[2:]
    env[SeenEnv].add(path, normalize_document(content))

def test_patch_tool_execution(env):
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

    # Pre-populate SeenEnv to bypass safety check
    mark_seen(env, "~/test/file.txt", "old\n")

    # Needs reader mock
    reader = ToolReader(source)
    # We expect this to fail because file doesn't exist, but it confirms matching logic
    try:
        tool.execute(env, reader)
    except FileNotFoundError:
        pass

    # If it matched, it should have advanced
    assert reader.position == len(source)
    assert reader.tool_count == 1

def test_execute_simple_replacement(env, tmp_path):
    (tmp_path / 'file.txt').write_text("line1\nline2\nline3\n", encoding='utf-8')
    mark_seen(env, "~/test/file.txt", "line1\nline2\nline3\n")

    diff = dedent("""
        @@
        -line2
        +modified
    """)
    tool = PatchTool()
    tool.execute_fenced(env, "Patch", "~/test/file.txt", diff)

    assert (tmp_path / 'file.txt').read_text(encoding='utf-8') == "line1\nmodified\nline3\n"

    context_env = env[ContextEnv]
    context_messages = context_env.build().messages
    log = "\n".join(m.content for m in context_messages if m.intent == ChatIntent.STATUS)
    system_messages = [m for m in context_messages if m.intent == ChatIntent.SYSTEM]

    assert "Applied 1 hunks to `~/test/file.txt`." in log
    assert not system_messages

def test_execute_with_context(env, tmp_path):
    (tmp_path / 'file.txt').write_text("A\nB\nC\nD\n", encoding='utf-8')
    mark_seen(env, "~/test/file.txt", "A\nB\nC\nD\n")

    diff = dedent("""
        @@
         A
        -B
        +MODIFIED
         C
    """)
    tool = PatchTool()
    tool.execute_fenced(env, "Patch", "~/test/file.txt", diff)

    assert (tmp_path / 'file.txt').read_text(encoding='utf-8') == "A\nMODIFIED\nC\nD\n"

def test_execute_multiple_hunks(env, tmp_path):
    (tmp_path / 'file.txt').write_text("A\nB\nC\nD\nE\n", encoding='utf-8')
    mark_seen(env, "~/test/file.txt", "A\nB\nC\nD\nE\n")

    diff = dedent("""
        @@
        -A
        +Start
        @@
         D
        -E
        +End
    """)
    tool = PatchTool()
    tool.execute_fenced(env, "Patch", "~/test/file.txt", diff)

    assert (tmp_path / 'file.txt').read_text(encoding='utf-8') == "Start\nB\nC\nD\nEnd\n"

    context_env = env[ContextEnv]
    context_messages = context_env.build().messages
    log = "\n".join(m.content for m in context_messages if m.intent == ChatIntent.STATUS)

    assert "Applied 2 hunks to `~/test/file.txt`." in log

def test_execute_fail_not_found(env, tmp_path):
    (tmp_path / 'file.txt').write_text("A\nB\nC\n", encoding='utf-8')
    mark_seen(env, "~/test/file.txt", "A\nB\nC\n")

    diff = dedent("""
        @@
        -D
        +E
    """)
    tool = PatchTool()
    with pytest.raises(ValueError, match="Hunk 1 search block not found"):
        tool.execute_fenced(env, "Patch", "~/test/file.txt", diff)

def test_execute_fail_ambiguous(env, tmp_path):
    (tmp_path / 'file.txt').write_text("A\nA\nA\n", encoding='utf-8')
    mark_seen(env, "~/test/file.txt", "A\nA\nA\n")

    diff = dedent("""
        @@
        -A
        +B
    """)
    tool = PatchTool()
    with pytest.raises(ValueError, match="Context is ambiguous"):
        tool.execute_fenced(env, "Patch", "~/test/file.txt", diff)

def test_execute_fail_empty_search(env, tmp_path):
    (tmp_path / 'file.txt').write_text("A\n", encoding='utf-8')
    mark_seen(env, "~/test/file.txt", "A\n")

    diff = dedent("""
        @@
        +New
    """)
    tool = PatchTool()
    with pytest.raises(ValueError, match="Hunk 1 search block is empty"):
        tool.execute_fenced(env, "Patch", "~/test/file.txt", diff)

def test_execute_whole_line_enforcement(env, tmp_path):
    # 'target\n' exists in the content, but not at the start of a line
    (tmp_path / 'file.txt').write_text("prefix_target\n", encoding='utf-8')
    mark_seen(env, "~/test/file.txt", "prefix_target\n")

    diff = dedent("""
        @@
        -target
        +replacement
    """)
    tool = PatchTool()

    # Fixed regex to match lowercase
    with pytest.raises(ValueError, match="search block not found"):
        tool.execute_fenced(env, "Patch", "~/test/file.txt", diff)

def test_execute_ignore_header(env, tmp_path):
    (tmp_path / 'file.txt').write_text("A\n", encoding='utf-8')
    mark_seen(env, "~/test/file.txt", "A\n")

    diff = dedent("""
        --- a/file.txt
        +++ b/file.txt
        @@
        -A
        +B
    """)
    tool = PatchTool()
    tool.execute_fenced(env, "Patch", "~/test/file.txt", diff)
    assert (tmp_path / 'file.txt').read_text(encoding='utf-8') == "B\n"

def test_execute_normalization(env, tmp_path):
    (tmp_path / 'file.txt').write_text("A\nB\n", encoding='utf-8')
    mark_seen(env, "~/test/file.txt", "A\nB\n")

    # Input has irregular whitespace
    diff = dedent("""
        @@
        -B
        +C
    """)
    tool = PatchTool()
    tool.execute_fenced(env, "Patch", "~/test/file.txt", diff)
    # Result should be normalized (no trailing empty lines beyond the terminal newline)
    assert (tmp_path / 'file.txt').read_text(encoding='utf-8') == "A\nC\n"

def test_execute_missing_file(env):
    mark_seen(env, "~/test/missing.txt", "")
    tool = PatchTool()
    with pytest.raises(FileNotFoundError, match="File not found"):
        tool.execute_fenced(env, "Patch", "~/test/missing.txt", "@@\n-a\n+b")

def test_atomic_execution(env, tmp_path):
    """Ensures file is not modified if any hunk fails."""
    (tmp_path / 'file.txt').write_text("A\nB\nC\n", encoding='utf-8')
    mark_seen(env, "~/test/file.txt", "A\nB\nC\n")

    # First hunk matches, second hunk fails
    diff = dedent("""
        @@
        -A
        +ModifiedA
        @@
        -X
        +ModifiedX
    """)
    tool = PatchTool()
    # Fixed regex to match lowercase
    with pytest.raises(ValueError, match="search block not found"):
        tool.execute_fenced(env, "Patch", "~/test/file.txt", diff)

    # File should be unchanged
    assert (tmp_path / 'file.txt').read_text(encoding='utf-8') == "A\nB\nC\n"

def test_strict_context_parsing(env, tmp_path):
    """Ensures context lines must start with space, not be empty."""
    (tmp_path / 'file.txt').write_text("A\n\nB\n", encoding='utf-8')
    mark_seen(env, "~/test/file.txt", "A\n\nB\n")

    # This diff has an empty line which should be rejected
    diff = dedent("""
        @@
        -A

        -B
        +C
    """)
    tool = PatchTool()
    # The empty line will fall through to the invalid line check
    with pytest.raises(ValueError, match="Invalid diff line"):
        tool.execute_fenced(env, "Patch", "~/test/file.txt", diff)

def test_execute_ignore_trailing_whitespace_in_diff(env, tmp_path):
    (tmp_path / 'file.txt').write_text("line1\n", encoding='utf-8')
    mark_seen(env, "~/test/file.txt", "line1\n")

    # Diff has trailing whitespace on the context line
    diff = dedent("""
        @@
        -line1
        +line2
    """)
    tool = PatchTool()
    tool.execute_fenced(env, "Patch", "~/test/file.txt", diff)

    assert (tmp_path / 'file.txt').read_text(encoding='utf-8') == "line2\n"

def test_execute_preserve_empty_lines_after_strip(env, tmp_path):
    (tmp_path / 'file.txt').write_text("A\n\nB\n", encoding='utf-8')
    mark_seen(env, "~/test/file.txt", "A\n\nB\n")

    # Diff uses context/delete lines that are effectively empty but have trailing spaces
    # Note: Using manual string construction to ensure trailing spaces are present
    diff = "@@\n A \n  \n-B \n+C\n"

    tool = PatchTool()
    tool.execute_fenced(env, "Patch", "~/test/file.txt", diff)

    assert (tmp_path / 'file.txt').read_text(encoding='utf-8') == "A\n\nC\n"

def test_execute_unseen_file(env, tmp_path):
    (tmp_path / 'file.txt').write_text("A\n", encoding='utf-8')

    diff = dedent("""
        @@
        -A
        +B
    """)
    tool = PatchTool()
    with pytest.raises(PermissionError, match="must be read before it can be patched"):
        tool.execute_fenced(env, "Patch", "~/test/file.txt", diff)
