from pathlib import Path
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.chats.stream import record_stream
from llobot.chats.thread import ChatThread
from llobot.models.echo import EchoModel
from llobot.projects.library.home import HomeProjectLibrary
from llobot.roles.editor import Editor
from llobot.utils.fs import write_text

def get_response_content(thread: ChatThread) -> str:
    """Helper to extract model response content from the thread."""
    for msg in thread:
        if msg.intent == ChatIntent.RESPONSE:
            return msg.content
    return ""

def setup_test_project(tmp_path: Path) -> tuple[Path, HomeProjectLibrary]:
    """Sets up a test project with files."""
    projects_dir = tmp_path / "projects"
    project_a = projects_dir / "project_a"
    project_a.mkdir(parents=True)
    write_text(project_a / "README.md", "# Project A")
    project_a.joinpath("src").mkdir()
    write_text(project_a / "src" / "main.py", "print('hello')")
    project_a.joinpath("tests").mkdir()
    write_text(project_a / "tests" / "test_main.py", "def test(): pass")

    library = HomeProjectLibrary(projects_dir)
    return projects_dir, library

def test_editor_project_selection(tmp_path: Path):
    """Tests that Editor includes file index when a project is selected."""
    projects_dir, library = setup_test_project(tmp_path)
    model = EchoModel('echo')
    editor = Editor('editor', model, projects=library, session_history=tmp_path / "sessions")

    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "@project_a List files")])
    response = get_response_content(record_stream(editor.chat(prompt)))

    # The index should list files
    assert "- README.md" in response
    assert "- src/" in response
    assert "- main.py" in response

def test_editor_file_retrieval(tmp_path: Path):
    """Tests that Editor retrieves specific files when mentioned."""
    projects_dir, library = setup_test_project(tmp_path)
    model = EchoModel('echo')
    editor = Editor('editor', model, projects=library, session_history=tmp_path / "sessions")

    # Select project and retrieve a specific file
    prompt1 = ChatThread([ChatMessage(ChatIntent.PROMPT, "@project_a @src/main.py Read code")])
    thread1 = record_stream(editor.chat(prompt1))
    response1 = get_response_content(thread1)

    # The content should be present
    assert "File: project_a/src/main.py" in response1
    assert "print('hello')" in response1

def test_editor_wildcard_retrieval(tmp_path: Path):
    """Tests that Editor retrieves files matching wildcard patterns."""
    projects_dir, library = setup_test_project(tmp_path)
    model = EchoModel('echo')
    editor = Editor('editor', model, projects=library, session_history=tmp_path / "sessions")

    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "@project_a @tests/*.py Read tests")])
    response = get_response_content(record_stream(editor.chat(prompt)))

    assert "File: project_a/tests/test_main.py" in response
    assert "def test(): pass" in response

def test_editor_overviews(tmp_path: Path):
    """Tests that Editor automatically includes ancestor overview files."""
    projects_dir = tmp_path / "projects"
    project_b = projects_dir / "project_b"
    project_b.mkdir(parents=True)
    (project_b / "doc").mkdir()
    write_text(project_b / "README.md", "Main Overview")
    write_text(project_b / "doc" / "README.md", "Doc Overview")
    write_text(project_b / "doc" / "api.py", "def api(): pass")

    library = HomeProjectLibrary(projects_dir)
    model = EchoModel('echo')
    editor = Editor('editor', model, projects=library, session_history=tmp_path / "sessions")

    # Access a file deep in the hierarchy
    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "@project_b @doc/api.py")])
    response = get_response_content(record_stream(editor.chat(prompt)))

    # Check that overviews are pulled in automatically
    assert "File: project_b/README.md" in response
    assert "Main Overview" in response
    assert "File: project_b/doc/README.md" in response
    assert "Doc Overview" in response
    assert "File: project_b/doc/api.py" in response

def test_editor_system_prompt(tmp_path: Path):
    """Tests that Editor includes the tool usage instructions in its prompt."""
    projects_dir, library = setup_test_project(tmp_path)
    model = EchoModel('echo')
    editor = Editor('editor', model, projects=library, session_history=tmp_path / "sessions")
    prompt = ChatThread([ChatMessage(ChatIntent.PROMPT, "@project_a some prompt")])
    response = get_response_content(record_stream(editor.chat(prompt)))

    assert "File manipulation tools" in response
    assert "New or modified file" in response
    assert "Removed file" in response
    assert "Moved file" in response
