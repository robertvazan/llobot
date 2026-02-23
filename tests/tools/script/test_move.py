from pathlib import Path, PurePosixPath
import pytest
from llobot.chats.intent import ChatIntent
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.environments.projects import ProjectEnv
from llobot.projects.directory import DirectoryProject
from llobot.projects.library.predefined import PredefinedProjectLibrary
from llobot.tools.script.move import ScriptMove

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

def test_move_tool_execute(env: Environment):
    tool = ScriptMove()
    assert tool.execute(env, "mv ~/myproject/a.txt ~/myproject/b.txt")

    project = env[ProjectEnv].union
    assert project.read(PurePosixPath("myproject/a.txt")) is None
    assert project.read(PurePosixPath("myproject/b.txt")) == "content\n"

def test_move_tool_overwrite(env: Environment):
    project = env[ProjectEnv].union
    project.write(PurePosixPath("myproject/b.txt"), "old content")
    tool = ScriptMove()
    tool.execute(env, "mv ~/myproject/a.txt ~/myproject/b.txt")
    log = "\n".join(m.content for m in env[ContextEnv].build().messages if m.intent == ChatIntent.SYSTEM)
    assert "Moved `~/myproject/a.txt` to `~/myproject/b.txt` (overwriting `~/myproject/b.txt`)" in log
    assert project.read(PurePosixPath("myproject/b.txt")) == "content\n"

def test_move_tool_no_match(env: Environment):
    tool = ScriptMove()
    assert not tool.execute(env, "cp a b")
    assert not tool.execute(env, "mv a b c")

def test_move_tool_missing_tilde(env: Environment):
    tool = ScriptMove()
    line = "mv myproject/a.txt ~/myproject/b.txt"
    with pytest.raises(ValueError, match="Path must start with ~/"):
        tool.execute(env, line)
