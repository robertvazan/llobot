from pathlib import PurePosixPath
from llobot.environments.knowledge import KnowledgeEnv

def test_knowledge_env(tmp_path):
    env = KnowledgeEnv()

    # Test initial state
    assert "file1.txt" not in env
    assert env.get("file1.txt") is None

    # Test adding content
    env.add("file1.txt", "content1")
    assert "file1.txt" in env
    assert env.get("file1.txt") == "content1"

    # Test path normalization
    assert "file1.txt" in env
    assert PurePosixPath("file1.txt") in env

    # Test updating content
    env.add("file1.txt", "content1_updated")
    assert env.get("file1.txt") == "content1_updated"

    # Test saving and loading
    save_dir = tmp_path / "session"
    env.save(save_dir)

    env2 = KnowledgeEnv()
    env2.load(save_dir)

    assert "file1.txt" in env2
    assert env2.get("file1.txt") == "content1_updated"

    # Test multiple files
    env.add("dir/file2.txt", "content2")
    env.save(save_dir)

    env3 = KnowledgeEnv()
    env3.load(save_dir)
    assert env3.get("file1.txt") == "content1_updated"
    assert env3.get("dir/file2.txt") == "content2"
