from pathlib import Path, PurePosixPath
import pytest
from llobot.environments import Environment
from llobot.environments.projects import ProjectEnv
from llobot.environments.context import ContextEnv
from llobot.projects.directory import DirectoryProject
from llobot.projects.library.predefined import PredefinedProjectLibrary
from llobot.tools.script.remove import ScriptRemove, ScriptRemoveCall

@pytest.fixture
def project(tmp_path: Path) -> DirectoryProject:
    proj_dir = tmp_path / "myproject"
    proj_dir.mkdir()
    (proj_dir / "a.txt").write_text("content")
    return DirectoryProject(proj_dir, prefix="myproject", mutable=True)

@pytest.fixture
def library(project: DirectoryProject) -> PredefinedProjectLibrary:
    return PredefinedProjectLibrary({"myproject": project})

@pytest.fixture
def env(library: PredefinedProjectLibrary) -> Environment:
    environment = Environment()
    penv = environment[ProjectEnv]
    penv.configure(library)
    penv.add("myproject")
    return environment

def test_remove_tool_matches_and_parses_line(env: Environment):
    tool = ScriptRemove()
    line = "rm ~/myproject/a.txt"

    assert tool.matches(env, line)

    call = tool.parse(env, line)
    assert isinstance(call, ScriptRemoveCall)
    assert call._path == "~/myproject/a.txt"

def test_remove_tool_quoted_path(env: Environment):
    tool = ScriptRemove()
    line = "rm \"~/myproject/foo bar.txt\""

    assert tool.matches(env, line)

    call = tool.parse(env, line)
    assert isinstance(call, ScriptRemoveCall)
    assert call._path == "~/myproject/foo bar.txt"

def test_remove_tool_execute(env: Environment):
    call = ScriptRemoveCall("~/myproject/a.txt")
    call.execute(env)

    project = env[ProjectEnv].union
    assert project.read(PurePosixPath("myproject/a.txt")) is None
    assert "Removed `~/myproject/a.txt`" in env[ContextEnv].build().messages[0].content

def test_remove_tool_no_match(env: Environment):
    tool = ScriptRemove()
    assert not tool.matches(env, "del a")
    assert not tool.matches(env, "rm a b")
