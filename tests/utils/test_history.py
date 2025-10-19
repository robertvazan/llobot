from datetime import timedelta
from llobot.utils.time import current_time
from llobot.utils.history import (
    format_history_filename, format_history_path, parse_history_path,
    try_parse_history_path, iterate_history, recent_history_paths,
    last_history_path
)

def test_format_and_parse(tmp_path):
    now = current_time()
    filename = format_history_filename(now, ".txt")
    assert filename.name.endswith(".txt")

    path = format_history_path(tmp_path, now, ".md")
    assert path.parent == tmp_path

    parsed = parse_history_path(path)
    assert parsed == now

    try_parsed = try_parse_history_path(path)
    assert try_parsed == now

    assert try_parse_history_path("invalid") is None

def test_history_iteration(tmp_path):
    now = current_time()
    t1 = now - timedelta(seconds=2)
    t2 = now - timedelta(seconds=1)
    t3 = now

    p1 = format_history_path(tmp_path, t1, ".log")
    p1.touch()
    p2 = format_history_path(tmp_path, t2, ".log")
    p2.touch()
    p3 = format_history_path(tmp_path, t3, ".log")
    p3.touch()
    (tmp_path / "not-a-history-file.txt").touch()

    all_history_files = sorted(list(iterate_history(tmp_path, ".log")))
    assert all_history_files == [p1, p2, p3]

    recent = list(recent_history_paths(tmp_path, ".log"))
    assert recent == [p3, p2, p1]

    recent_cutoff = list(recent_history_paths(tmp_path, ".log", cutoff=t2))
    assert recent_cutoff == [p2, p1]

    last = last_history_path(tmp_path, ".log")
    assert last == p3

    last_cutoff = last_history_path(tmp_path, ".log", cutoff=t1)
    assert last_cutoff == p1

    assert last_history_path(tmp_path, ".log", cutoff=now - timedelta(days=1)) is None
