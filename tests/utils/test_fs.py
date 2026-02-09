"""Tests for filesystem utilities."""
from pathlib import Path, PurePosixPath
import pytest
from llobot.utils.fs import (
    user_home, data_home, cache_home, create_parents,
    write_bytes, write_text, read_text, read_document, path_stem
)

def test_home_paths():
    assert user_home() == Path.home()
    assert data_home() == Path.home() / '.local/share'
    assert cache_home() == Path.home() / '.cache'

def test_file_io(tmp_path: Path):
    test_dir = tmp_path / "test"
    test_file = test_dir / "file.txt"

    # create_parents
    create_parents(test_file)
    assert test_dir.is_dir()

    # write_bytes
    write_bytes(test_file, b"hello")
    assert test_file.read_bytes() == b"hello"

    # write_text/read_text
    write_text(test_file, "world")
    assert read_text(test_file) == "world"

    # read_document
    write_text(test_file, "  doc\ncontent  \n\n")
    assert read_document(test_file) == "  doc\ncontent\n"

def test_read_text_strictness(tmp_path: Path):
    f = tmp_path / "test.txt"

    # Invalid UTF-8
    f.write_bytes(b"\xff")
    with pytest.raises(ValueError):
        read_text(f)

    # Control characters (e.g., null byte)
    f.write_bytes(b"hello\x00world")
    with pytest.raises(ValueError, match="Control characters"):
        read_text(f)

    # Allowed control characters (TAB, LF)
    f.write_text("hello\tworld\n", encoding='utf-8')
    assert read_text(f) == "hello\tworld\n"

    # CR translation
    f.write_bytes(b"hello\rworld")
    # Universal newlines should translate \r to \n
    assert read_text(f) == "hello\nworld"

def test_path_stem():
    assert path_stem("a/b/c.tar.gz") == "c"
    assert path_stem(Path("a/b/c.tar.gz")) == "c"
    assert path_stem(PurePosixPath("a/b/c.tar.gz")) == "c"
    assert path_stem("file.txt") == "file"
    assert path_stem("file") == "file"
    assert path_stem(".bashrc") == ".bashrc"
