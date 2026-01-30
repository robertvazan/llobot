from pathlib import PurePosixPath
from llobot.chats.intent import ChatIntent
from llobot.crammers.tree.full import FullTreeCrammer
from llobot.environments.context import ContextEnv
from llobot.projects.items import ProjectLink

def test_cram_structure(setup_env_fixture):
    """Tests the structure of the rendered tree."""
    crammer = FullTreeCrammer()
    env = setup_env_fixture(["a/b", "a/c", "d"])

    crammer.cram(env)

    message = env[ContextEnv].builder.build().messages[0]
    assert message.intent == ChatIntent.SYSTEM
    content = message.content

    assert "~/.:" not in content
    assert "~/a:" in content
    assert "d" in content
    assert "b" in content
    assert "c" in content

def test_cram_links(setup_env_fixture):
    """Tests rendering of symlinks."""
    crammer = FullTreeCrammer()
    link = ProjectLink(PurePosixPath("link"), PurePosixPath("target"))
    env = setup_env_fixture([link])

    crammer.cram(env)

    content = env[ContextEnv].builder.build().messages[0].content
    assert "link -> target" in content

def test_cram_empty(setup_env_fixture):
    """Tests that nothing is added for empty project."""
    crammer = FullTreeCrammer()
    env = setup_env_fixture([])

    crammer.cram(env)
    assert not env[ContextEnv].builder.build()

def test_cram_ignores_budget(setup_env_fixture):
    """Tests that budget is ignored."""
    crammer = FullTreeCrammer()
    env = setup_env_fixture(["file.txt"])
    # Set budget to very small
    env[ContextEnv].builder.budget = 1

    crammer.cram(env)

    # It should still have added the message
    assert env[ContextEnv].builder.build()
