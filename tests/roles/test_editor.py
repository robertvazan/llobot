from pathlib import Path
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.stream import record_stream
from llobot.chats.thread import ChatThread
from tests.models.mock import MockModel
from llobot.projects.directory import DirectoryProject
from llobot.projects.library.predefined import PredefinedProjectLibrary
from llobot.roles.editor import Editor
from llobot.utils.fs import write_text

def setup_test_project(tmp_path: Path) -> tuple[Path, PredefinedProjectLibrary]:
    """Sets up a test project with files."""
    project_a_dir = tmp_path / "project_a"
    project_a_dir.mkdir(parents=True)
    write_text(project_a_dir / "README.md", "# Project A")
    project_a_dir.joinpath("src").mkdir()
    write_text(project_a_dir / "src" / "main.py", "print('hello')")
    project_a_dir.joinpath("tests").mkdir()
    write_text(project_a_dir / "tests" / "test_main.py", "def test(): pass")

    project_a = DirectoryProject(project_a_dir, prefix="project_a")
    library = PredefinedProjectLibrary({"project_a": project_a})
    return project_a_dir, library

def test_editor_project_selection(tmp_path: Path):
    """Tests that Editor includes file index when a project is selected."""
    _, library = setup_test_project(tmp_path)
    model = MockModel('echo')
    editor = Editor('editor', model, projects=library, session_history=tmp_path / "sessions")

    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "@project_a List files")])
    record_stream(editor.chat(prompt))
    context = model.history[0]

    # The index should list files
    assert "~/project_a:" in context
    assert "README.md" in context
    assert "src/" in context
    assert "~/project_a/src:" in context
    assert "main.py" in context

def test_editor_file_retrieval(tmp_path: Path):
    """Tests that Editor retrieves specific files when mentioned."""
    _, library = setup_test_project(tmp_path)
    model = MockModel('echo')
    editor = Editor('editor', model, projects=library, session_history=tmp_path / "sessions")

    # Select project and retrieve a specific file
    prompt1 = ChatThread([ChatMessage(ChatIntent.PROMPT, "@project_a @src/main.py Read code")])
    record_stream(editor.chat(prompt1))
    context = model.history[0]

    # The content should be present
    assert "File: ~/project_a/src/main.py" in context
    assert "print('hello')" in context

def test_editor_wildcard_retrieval(tmp_path: Path):
    """Tests that Editor retrieves files matching wildcard patterns."""
    _, library = setup_test_project(tmp_path)
    model = MockModel('echo')
    editor = Editor('editor', model, projects=library, session_history=tmp_path / "sessions")

    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "@project_a @tests/*.py Read tests")])
    record_stream(editor.chat(prompt))
    context = model.history[0]

    assert "File: ~/project_a/tests/test_main.py" in context
    assert "def test(): pass" in context

def test_editor_overviews(tmp_path: Path):
    """Tests that Editor automatically includes ancestor overview files."""
    project_b_dir = tmp_path / "project_b"
    project_b_dir.mkdir(parents=True)
    (project_b_dir / "doc").mkdir()
    write_text(project_b_dir / "README.md", "Main Overview")
    write_text(project_b_dir / "doc" / "README.md", "Doc Overview")
    write_text(project_b_dir / "doc" / "api.py", "def api(): pass")

    project_b = DirectoryProject(project_b_dir, prefix="project_b")
    library = PredefinedProjectLibrary({"project_b": project_b})
    model = MockModel('echo')
    editor = Editor('editor', model, projects=library, session_history=tmp_path / "sessions")

    # Access a file deep in the hierarchy
    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "@project_b @doc/api.py")])
    record_stream(editor.chat(prompt))
    context = model.history[0]

    # Check that overviews are pulled in automatically
    assert "File: ~/project_b/README.md" in context
    assert "Main Overview" in context
    assert "File: ~/project_b/doc/README.md" in context
    assert "Doc Overview" in context
    assert "File: ~/project_b/doc/api.py" in context

def test_editor_system_prompt(tmp_path: Path):
    """Tests that Editor includes the tool usage instructions in its prompt."""
    _, library = setup_test_project(tmp_path)
    model = MockModel('echo')
    editor = Editor('editor', model, projects=library, session_history=tmp_path / "sessions")
    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "@project_a some prompt")])
    record_stream(editor.chat(prompt))
    context = model.history[0]
    assert "Assistant editor's guidelines" in context
    assert "How to ask questions" in context
    assert "How to write closing remarks" in context
