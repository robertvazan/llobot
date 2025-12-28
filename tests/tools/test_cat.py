from pathlib import Path, PurePosixPath
import pytest
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.projects import ProjectEnv
from llobot.environments.tools import ToolEnv
from llobot.formats.documents import standard_document_format
from llobot.projects.directory import DirectoryProject
from llobot.projects.library.home import HomeProjectLibrary
from llobot.tools.cat import CatTool, CatToolCall
from llobot.knowledge.subsets.standard import overviews_subset

@pytest.fixture
def home_library(tmp_path: Path) -> HomeProjectLibrary:
    return HomeProjectLibrary(str(tmp_path), mutable=True)

@pytest.fixture
def project(home_library: HomeProjectLibrary, tmp_path: Path) -> DirectoryProject:
    proj_dir = tmp_path / "myproject"
    proj_dir.mkdir()
    (proj_dir / "a.txt").write_text("content")
    (proj_dir / "b.py").write_text("print('hello')")
    (proj_dir / "README.md").write_text("# Readme")

    sub_dir = proj_dir / "sub"
    sub_dir.mkdir()
    (sub_dir / "c.txt").write_text("subcontent")
    (sub_dir / "__init__.py").write_text("# Init")

    projects = home_library.lookup("myproject")
    assert projects and isinstance(projects[0], DirectoryProject)
    return projects[0]

@pytest.fixture
def env(home_library: HomeProjectLibrary, project: DirectoryProject) -> Environment:
    environment = Environment()
    penv = environment[ProjectEnv]
    penv.configure(home_library)
    penv.add("myproject")
    return environment

def test_cat_tool_matches_and_parses_line(env: Environment):
    tool = CatTool()
    line = "cat ~/myproject/a.txt"

    assert tool.matches_line(env, line)

    call = tool.parse_line(env, line)
    assert isinstance(call, CatToolCall)
    assert call._path == PurePosixPath("myproject/a.txt")

def test_cat_tool_execute(env: Environment):
    call = CatToolCall(PurePosixPath("myproject/a.txt"), standard_document_format(), overviews_subset())
    call.execute(env)

    log = env[ToolEnv].flush_log()
    output = env[ToolEnv].flush_output()

    assert "Preparing to read ~/myproject/a.txt..." in log
    assert "Scanning ~/myproject for overviews..." in log
    assert "Reading ~/myproject/README.md..." in log
    assert "Reading ~/myproject/a.txt..." in log
    assert "File was read." in log

    assert "File: ~/myproject/README.md" in output
    assert "# Readme" in output
    assert "File: ~/myproject/a.txt" in output
    assert "content" in output

def test_cat_tool_execute_nested_overviews(env: Environment):
    call = CatToolCall(PurePosixPath("myproject/sub/c.txt"), standard_document_format(), overviews_subset())
    call.execute(env)

    log = env[ToolEnv].flush_log()
    output = env[ToolEnv].flush_output()

    indices = [
        log.find("Preparing to read ~/myproject/sub/c.txt..."),
        log.find("Scanning ~/myproject for overviews..."),
        log.find("Reading ~/myproject/README.md..."),
        log.find("Scanning ~/myproject/sub for overviews..."),
        log.find("Reading ~/myproject/sub/__init__.py..."),
        log.find("Reading ~/myproject/sub/c.txt..."),
    ]
    assert -1 not in indices
    assert indices == sorted(indices)

def test_cat_tool_execute_deduplication(env: Environment):
    # Pre-populate context with the file content
    listing = standard_document_format().render(PurePosixPath("myproject/a.txt"), "content")
    env[ContextEnv].add(ChatMessage(ChatIntent.SYSTEM, listing))

    call = CatToolCall(PurePosixPath("myproject/a.txt"), standard_document_format(), overviews_subset())
    call.execute(env)

    log = env[ToolEnv].flush_log()
    output = env[ToolEnv].flush_output()

    assert "Preparing to read ~/myproject/a.txt..." in log
    assert "Scanning ~/myproject for overviews..." in log
    assert "Reading ~/myproject/README.md..." in log
    assert "Reading ~/myproject/a.txt..." in log
    assert "File myproject/a.txt is already in the context." in log

    assert "File: ~/myproject/README.md" in output
    assert "content" not in output

def test_cat_tool_overview_deduplication(env: Environment):
    # Pre-populate context with the overview content
    listing = standard_document_format().render(PurePosixPath("myproject/README.md"), "# Readme")
    env[ContextEnv].add(ChatMessage(ChatIntent.SYSTEM, listing))

    call = CatToolCall(PurePosixPath("myproject/a.txt"), standard_document_format(), overviews_subset())
    call.execute(env)

    log = env[ToolEnv].flush_log()

    assert "Preparing to read ~/myproject/a.txt..." in log
    assert "Scanning ~/myproject for overviews..." in log
    assert "Reading ~/myproject/README.md..." in log
    assert "File myproject/README.md is already in the context." in log
    assert "Reading ~/myproject/a.txt..." in log

def test_cat_tool_execute_python(env: Environment):
    call = CatToolCall(PurePosixPath("myproject/b.py"), standard_document_format(), overviews_subset())
    call.execute(env)

    output = env[ToolEnv].flush_output()
    # ExtensionLanguageMapping maps .py to python
    assert "```python" in output
    assert "print('hello')" in output

def test_cat_tool_missing_file_loads_overviews(env: Environment):
    call = CatToolCall(PurePosixPath("myproject/nonexistent.txt"), standard_document_format(), overviews_subset())
    with pytest.raises(ValueError, match="File not found"):
        call.execute(env)

    log = env[ToolEnv].flush_log()
    output = env[ToolEnv].flush_output()

    assert "Preparing to read ~/myproject/nonexistent.txt..." in log
    assert "Scanning ~/myproject for overviews..." in log
    assert "Reading ~/myproject/README.md..." in log
    assert "Reading ~/myproject/nonexistent.txt..." in log
    assert "File: ~/myproject/README.md" in output

def test_cat_tool_target_is_overview(env: Environment):
    # If we cat the overview itself, it should appear once
    call = CatToolCall(PurePosixPath("myproject/README.md"), standard_document_format(), overviews_subset())
    call.execute(env)

    log = env[ToolEnv].flush_log()
    output = env[ToolEnv].flush_output()

    # Should read it only once
    assert log.count("Reading ~/myproject/README.md...") == 1
    assert "File is already in the context." not in log
    assert output.count("# Readme") == 1

def test_cat_tool_no_match(env: Environment):
    tool = CatTool()
    assert not tool.matches_line(env, "read a")
    assert not tool.matches_line(env, "cat a b")
