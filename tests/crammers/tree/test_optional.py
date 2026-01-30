from pathlib import PurePosixPath
from llobot.chats.intent import ChatIntent
from llobot.crammers.tree.optional import OptionalTreeCrammer
from llobot.environments.context import ContextEnv
from llobot.projects.items import ProjectLink

def test_cram_fits(setup_env_fixture):
    """Tests that the tree is added when it fits the budget."""
    crammer = OptionalTreeCrammer(budget=1000)
    env = setup_env_fixture(["prefix/file.txt"], prefixes=['prefix'])

    crammer.cram(env)

    thread = env[ContextEnv].builder.build()
    assert thread
    message = thread.messages[0]
    assert message.intent == ChatIntent.SYSTEM
    assert "file.txt" in message.content
    assert "~/prefix:" in message.content
    assert "~/.:" not in message.content

def test_cram_structure(setup_env_fixture):
    """Tests the structure of the rendered tree."""
    crammer = OptionalTreeCrammer(budget=1000)
    # Mock project that returns items in order
    env = setup_env_fixture(["a/b", "a/c", "d"])

    crammer.cram(env)

    content = env[ContextEnv].builder.build().messages[0].content

    # Expected groups:
    # d
    #
    # ~/a:
    # b
    # c

    assert "~/.:" not in content
    assert "~/a:" in content
    assert "d" in content
    assert "b" in content
    assert "c" in content

def test_cram_links(setup_env_fixture):
    """Tests rendering of symlinks."""
    crammer = OptionalTreeCrammer(budget=1000)
    link = ProjectLink(PurePosixPath("link"), PurePosixPath("target"))
    env = setup_env_fixture([link])

    crammer.cram(env)

    content = env[ContextEnv].builder.build().messages[0].content
    assert "link -> target" in content

def test_cram_does_not_fit(setup_env_fixture):
    """Tests that the tree is not added when it exceeds the budget."""
    crammer = OptionalTreeCrammer(budget=10)
    env = setup_env_fixture(["long_filename_that_exceeds_budget.txt"])

    crammer.cram(env)
    assert not env[ContextEnv].builder.build()

def test_cram_empty(setup_env_fixture):
    """Tests that nothing is added for empty project."""
    crammer = OptionalTreeCrammer(budget=1000)
    env = setup_env_fixture([])

    crammer.cram(env)
    assert not env[ContextEnv].builder.build()

def test_respects_budget(setup_env_fixture):
    """Tests that the budget is respected."""
    crammer = OptionalTreeCrammer(budget=1000)
    env = setup_env_fixture(["file.txt"])
    builder = env[ContextEnv].builder

    # Original test was checking if budget on builder is restored.
    # Now we check if crammer respects its budget.
    crammer.cram(env)
    assert builder.cost > 0

    # If budget is too small
    builder.undo(0)
    crammer_small = OptionalTreeCrammer(budget=1)
    crammer_small.cram(env)
    assert builder.cost == 0
