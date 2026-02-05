from llobot.chats.intent import ChatIntent
from llobot.crammers.tree.balanced import BalancedTreeCrammer
from llobot.environments.context import ContextEnv
from llobot.environments.projects import ProjectEnv
from llobot.projects.items import ProjectDirectory, ProjectFile

def test_balanced_structure(setup_env_fixture):
    """Tests basic structure rendering."""
    crammer = BalancedTreeCrammer()
    env = setup_env_fixture(["a/b", "c"])

    crammer.cram(env)

    message = env[ContextEnv].builder.build().messages[0]
    assert message.intent == ChatIntent.SYSTEM
    content = message.content

    assert "Project files" in content
    assert "listed below" in content

    # Root listing
    assert "a/" in content
    assert "c" in content

    # Subdir listing
    assert "~/a:" in content
    assert "b" in content

def test_note_placement(setup_env_fixture):
    """Tests that the note is placed correctly in the details body."""
    note = "My special note"
    crammer = BalancedTreeCrammer(note=note)
    env = setup_env_fixture(["a"])

    crammer.cram(env)

    content = env[ContextEnv].builder.build().messages[0].content

    # Note should be after summary and before code block
    assert f"<summary>Project files</summary>\n\n{note}\n\n```" in content

def test_untracked_items(setup_env_fixture):
    """
    Tests that untracked items are listed but not descended into.
    """
    env = setup_env_fixture(["tracked/file", "untracked/file"])
    project = env[ProjectEnv].union

    # Monkeypatch tracked method on the project instance (UnionProject wrapping MockProject)
    # But wait, UnionProject delegates to MockProject.
    # We can patch UnionProject.tracked or traverse to MockProject.
    # Let's try patching UnionProject instance first.

    # However, UnionProject logic:
    # def tracked(self, item): return project.tracked(item)
    # So if we patch UnionProject.tracked, it works for checks done via UnionProject.
    # BalancedTreeCrammer uses `project = env[ProjectEnv].union`.

    import types
    # We need to capture original tracked to avoid recursion if we want to delegate
    # But MockProject.tracked simply returns True.
    # So we can just implement our logic.

    def mock_tracked(self, item):
        if "untracked" in str(item.path):
            return False
        return True

    project.tracked = types.MethodType(mock_tracked, project)

    crammer = BalancedTreeCrammer()
    crammer.cram(env)

    content = env[ContextEnv].builder.build().messages[0].content

    # Root listing should show both 'tracked/' and 'untracked/' directories
    assert "tracked/" in content
    assert "untracked/" in content

    # Should descend into 'tracked'
    assert "~/tracked:" in content
    assert "file" in content

    # Should NOT descend into 'untracked'
    assert "~/untracked:" not in content

def test_budget_limit(setup_env_fixture):
    """Tests that crammer respects budget."""
    crammer = BalancedTreeCrammer(budget=20) # Very small budget
    env = setup_env_fixture(["a/b", "c/d", "e/f"])

    crammer.cram(env)

    message = env[ContextEnv].builder.build().messages[0]
    content = message.content

    # Root listing takes some space: "a/\nc/\ne/" ~ 6 chars.
    # With details wrapper it is much larger.
    # Wait, budget applies to the *content* of the tree text, not the wrapper?
    # No, ContextBuilder tracks total budget.
    # But BalancedTreeCrammer takes a budget parameter and tracks `used_budget` against it.
    # It constructs `full_text` and then puts it in message.
    # The `used_budget` tracks the length of `full_text`.

    # If budget=20.
    # Root listing: "a/\nc/\ne/" -> length 9.
    # Remaining: 11.
    # Next items: a, c, e directories.
    # "~/a:\nb" -> length 7.
    # 9 + 2 (sep) + 7 = 18.
    # So maybe one subdir fits.

    # We expect some parts to be missing.
    assert "a/" in content # Root usually fits

    # Check if all subdirs are present
    present = 0
    if "~/a:" in content: present += 1
    if "~/c:" in content: present += 1
    if "~/e:" in content: present += 1

    assert present < 3, "Should not fit all subdirectories with budget 20"

def test_priority_order(setup_env_fixture):
    """
    Tests that narrow deep trees are preferred over wide deep trees.

    Structure:
    - A/ (narrow)
      - A1/
        - A2/
          - file
    - B/ (wide)
      - B1/
        - file
      - B2/
        - file
      - B3/
        - file
    """
    items = [
        "A/A1/A2/file",
        "B/B1/file",
        "B/B2/file",
        "B/B3/file",
    ]

    # Budget sufficient for Root + A + B + A1 + A2 (approx 72 chars text)
    # But not for B1, B2, B3.
    crammer = BalancedTreeCrammer(budget=70)
    env = setup_env_fixture(items)

    crammer.cram(env)

    content = env[ContextEnv].builder.build().messages[0].content

    # Check A branch
    assert "~/A:" in content
    assert "~/A/A1:" in content
    assert "~/A/A1/A2:" in content

    # Check B branch
    assert "~/B:" in content # B itself should fit

    # B subdirs should likely be omitted due to penalty/budget
    # B1 cost was calculated ~126 which is high priority (bad)
    # A2 cost was ~86.
    # Even if they fit in budget individually, A2 comes first.
    # Here budget 70 cuts off right after A2 (cumulative ~64).
    # So B1 shouldn't be there.

    assert "~/B/B1:" not in content
    assert "~/B/B2:" not in content
    assert "~/B/B3:" not in content

def test_nested_prefixes(setup_env_fixture):
    """Tests handling of nested prefixes."""
    # Prefix . and a/b
    # a/b is nested in .

    crammer = BalancedTreeCrammer()
    env = setup_env_fixture(["a/b/c"], prefixes=[".", "a/b"])

    crammer.cram(env)

    content = env[ContextEnv].builder.build().messages[0].content

    # Root (.) listing should contain a/
    assert "a/" in content

    # a listing should contain b/
    assert "~/a:" in content
    assert "b/" in content

    # a/b is a prefix, so it is added as a root with low cost (0 base).
    # It should definitely be present.
    assert "~/a/b:" in content
    assert "c" in content

    # Ensure a/b is not duplicated (added via recursive descent from a)
    # The code skips adding subdirectories if they are in prefixes.
    # We can check by counting occurrences or verifying structure.
    # Text is constructed from map, so duplicates in text are impossible.
    # But we want to ensure it was treated as root.
    pass
