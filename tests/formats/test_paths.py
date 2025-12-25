from pathlib import Path, PurePosixPath
import pytest
from llobot.formats.paths import coerce_path, parse_path

def test_coerce_path_valid():
    assert coerce_path("file.txt") == PurePosixPath("file.txt")
    assert coerce_path(Path("file.txt")) == PurePosixPath("file.txt")
    assert coerce_path(PurePosixPath("dir/file.txt")) == PurePosixPath("dir/file.txt")
    assert coerce_path(".") == PurePosixPath(".")

def test_coerce_path_absolute():
    with pytest.raises(ValueError, match="Path must be relative"):
        coerce_path("/etc/passwd")
    with pytest.raises(ValueError, match="Path must be relative"):
        coerce_path(Path("/etc/passwd"))

def test_coerce_path_wildcards():
    with pytest.raises(ValueError, match="Path must not contain wildcards"):
        coerce_path("*.txt")
    with pytest.raises(ValueError, match="Path must not contain wildcards"):
        coerce_path("file?.txt")

def test_coerce_path_components():
    with pytest.raises(ValueError, match=r"Path must not contain '\.\.'"):
        coerce_path("../file.txt")
    with pytest.raises(ValueError, match=r"Path must not contain '\.\.'"):
        coerce_path("dir/..")
    with pytest.raises(ValueError, match="Path must not contain '~'"):
        coerce_path("~")
    with pytest.raises(ValueError, match="Path must not contain '~'"):
        coerce_path("dir/~/file")

def test_parse_path_valid():
    assert parse_path("~/file.txt") == PurePosixPath("file.txt")
    assert parse_path("~/dir/file.txt") == PurePosixPath("dir/file.txt")
    assert parse_path("~/dir/subdir/") == PurePosixPath("dir/subdir")
    assert parse_path("~/a-b_c.txt") == PurePosixPath("a-b_c.txt")

def test_parse_path_invalid_prefix():
    with pytest.raises(ValueError, match="Path must start with ~/"):
        parse_path("/file.txt")
    with pytest.raises(ValueError, match="Path must start with ~/"):
        parse_path("file.txt")
    with pytest.raises(ValueError, match="Path must start with ~/"):
        parse_path("~file.txt")

def test_parse_path_root():
    with pytest.raises(ValueError, match="Path cannot be the root directory"):
        parse_path("~/")
    with pytest.raises(ValueError, match="Path cannot be the root directory"):
        parse_path("~/.")

def test_parse_path_absolute_internal():
    with pytest.raises(ValueError, match="Path must be relative to project root"):
        parse_path("~//etc/passwd")

def test_parse_path_wildcards():
    with pytest.raises(ValueError, match="Path must not contain wildcards"):
        parse_path("~/*.txt")
    with pytest.raises(ValueError, match="Path must not contain wildcards"):
        parse_path("~/file?.txt")
    with pytest.raises(ValueError, match="Path must not contain wildcards"):
        parse_path("~/file[1].txt")

def test_parse_path_components():
    with pytest.raises(ValueError, match=r"Path must not contain '\.\.'"):
        parse_path("~/dir/../file.txt")
    with pytest.raises(ValueError, match=r"Path must not contain '\.\.'"):
        parse_path("~/..")
    with pytest.raises(ValueError, match="Path must not contain '~'"):
        parse_path("~/dir/~/file.txt")
