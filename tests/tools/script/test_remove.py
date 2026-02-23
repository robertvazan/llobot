from pathlib import Path, PurePosixPath
import pytest
from llobot.chats.intent import ChatIntent
from llobot.environments import Environment
from llobot.environments.projects import ProjectEnv
from llobot.environments.context import ContextEnv
from llobot.projects.directory import DirectoryProject
from llobot.projects.library.predefined import PredefinedProjectLibrary
from llobot.tools.script.remove import ScriptRemove

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

def test_remove_tool_execute(env: Environment):
    tool = ScriptRemove()
    assert tool.execute(env, "rm ~/myproject/a.txt")

    project = env[ProjectEnv].union
    assert project.read(PurePosixPath("myproject/a.txt")) is None
    msg = env[ContextEnv].build().messages[0]
    assert msg.intent == ChatIntent.SYSTEM
    assert "Removed `~/myproject/a.txt`" in msg.content

def test_remove_tool_no_match(env: Environment):
    tool = ScriptRemove()
    assert not tool.execute(env, "del a")
    assert not tool.execute(env, "rm a b")
