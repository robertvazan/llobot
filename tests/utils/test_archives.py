from datetime import timedelta
from llobot.utils.time import current_time
from llobot.utils.archives import (
    format_archive_filename, format_archive_path, parse_archive_path,
    try_parse_archive_path, iterate_archive, recent_archive_paths,
    last_archive_path
)

def test_format_and_parse(tmp_path):
    now = current_time()
    filename = format_archive_filename(now, ".txt")
    assert filename.name.endswith(".txt")

    path = format_archive_path(tmp_path, now, ".md")
    assert path.parent == tmp_path

    parsed = parse_archive_path(path)
    assert parsed == now

    try_parsed = try_parse_archive_path(path)
    assert try_parsed == now

    assert try_parse_archive_path("invalid") is None

def test_archive_iteration(tmp_path):
    now = current_time()
    t1 = now - timedelta(seconds=2)
    t2 = now - timedelta(seconds=1)
    t3 = now

    p1 = format_archive_path(tmp_path, t1, ".log")
    p1.touch()
    p2 = format_archive_path(tmp_path, t2, ".log")
    p2.touch()
    p3 = format_archive_path(tmp_path, t3, ".log")
    p3.touch()
    (tmp_path / "not-an-archive.txt").touch()

    all_archives = sorted(list(iterate_archive(tmp_path, ".log")))
    assert all_archives == [p1, p2, p3]

    recent = list(recent_archive_paths(tmp_path, ".log"))
    assert recent == [p3, p2, p1]

    recent_cutoff = list(recent_archive_paths(tmp_path, ".log", cutoff=t2))
    assert recent_cutoff == [p2, p1]

    last = last_archive_path(tmp_path, ".log")
    assert last == p3

    last_cutoff = last_archive_path(tmp_path, ".log", cutoff=t1)
    assert last_cutoff == p1

    assert last_archive_path(tmp_path, ".log", cutoff=now - timedelta(days=1)) is None
