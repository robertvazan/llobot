from llobot.environments.commands import CommandsEnv

def test_command_queue_add_single():
    """Tests adding a single command."""
    queue = CommandsEnv()
    queue.add("cmd1")
    assert queue.get() == ["cmd1"]

def test_command_queue_add_multiple():
    """Tests adding multiple commands from an iterable."""
    queue = CommandsEnv()
    queue.add(["cmd1", "cmd2"])
    assert queue.get() == ["cmd1", "cmd2"]

def test_command_queue_add_mixed():
    """Tests adding single and multiple commands."""
    queue = CommandsEnv()
    queue.add("cmd2")
    queue.add(["cmd1", "cmd3"])
    assert queue.get() == ["cmd1", "cmd2", "cmd3"]

def test_command_queue_duplicates():
    """Tests that duplicate commands are stored only once."""
    queue = CommandsEnv()
    queue.add("cmd1")
    queue.add("cmd1")
    queue.add(["cmd2", "cmd2"])
    assert queue.get() == ["cmd1", "cmd2"]

def test_command_queue_get_sorted():
    """Tests that get() returns a sorted list."""
    queue = CommandsEnv()
    queue.add(["cmd3", "cmd1", "cmd2"])
    assert queue.get() == ["cmd1", "cmd2", "cmd3"]

def test_command_queue_consume():
    """Tests consuming a command from the queue."""
    queue = CommandsEnv()
    queue.add(["cmd1", "cmd2", "cmd3"])
    queue.consume("cmd2")
    assert queue.get() == ["cmd1", "cmd3"]
    queue.consume("cmd1")
    assert queue.get() == ["cmd3"]
    queue.consume("cmd3")
    assert queue.get() == []

def test_command_queue_consume_nonexistent():
    """Tests that consuming a non-existent command does nothing."""
    queue = CommandsEnv()
    queue.add("cmd1")
    queue.consume("cmd2")
    assert queue.get() == ["cmd1"]
