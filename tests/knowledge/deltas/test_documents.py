from pathlib import Path
from llobot.knowledge.deltas import DocumentDelta

def test_init():
    delta = DocumentDelta(Path('file.txt'), 'content', new=True)
    expected = DocumentDelta(Path('file.txt'), 'content', new=True)
    assert delta == expected

def test_path():
    delta = DocumentDelta(Path('test/file.txt'), 'content')
    assert delta.path == Path('test/file.txt')

def test_new():
    delta_new = DocumentDelta(Path('file.txt'), 'content', new=True)
    assert delta_new.new

    delta_not_new = DocumentDelta(Path('file.txt'), 'content')
    assert not delta_not_new.new

def test_modified():
    delta_modified = DocumentDelta(Path('file.txt'), 'content', modified=True)
    assert delta_modified.modified

    delta_not_modified = DocumentDelta(Path('file.txt'), 'content')
    assert not delta_not_modified.modified

def test_removed():
    delta_removed = DocumentDelta(Path('file.txt'), None, removed=True)
    assert delta_removed.removed

    delta_not_removed = DocumentDelta(Path('file.txt'), 'content')
    assert not delta_not_removed.removed

def test_diff():
    delta_diff = DocumentDelta(Path('file.txt'), 'diff content', modified=True, diff=True)
    assert delta_diff.diff

    delta_not_diff = DocumentDelta(Path('file.txt'), 'content')
    assert not delta_not_diff.diff

def test_moved_from():
    old_path = Path('old.txt')
    delta_moved = DocumentDelta(Path('new.txt'), None, moved_from=old_path)
    assert delta_moved.moved_from == old_path

    delta_not_moved = DocumentDelta(Path('file.txt'), 'content')
    assert delta_not_moved.moved_from is None

def test_moved():
    delta_moved = DocumentDelta(Path('new.txt'), None, moved_from=Path('old.txt'))
    assert delta_moved.moved

    delta_not_moved = DocumentDelta(Path('file.txt'), 'content')
    assert not delta_not_moved.moved

def test_content():
    delta_with_content = DocumentDelta(Path('file.txt'), 'test content')
    assert delta_with_content.content == 'test content'

    delta_without_content = DocumentDelta(Path('file.txt'), None, removed=True)
    assert delta_without_content.content is None

def test_valid_combinations():
    # Valid: content with no flags
    assert DocumentDelta(Path('file.txt'), 'content').valid

    # Valid: new file
    assert DocumentDelta(Path('file.txt'), 'content', new=True).valid

    # Valid: modified file
    assert DocumentDelta(Path('file.txt'), 'content', modified=True).valid

    # Valid: removed file (no content)
    assert DocumentDelta(Path('file.txt'), None, removed=True).valid

    # Valid: moved file (no content)
    assert DocumentDelta(Path('new.txt'), None, moved_from=Path('old.txt')).valid

    # Valid: modified + moved
    assert DocumentDelta(Path('new.txt'), 'content', modified=True, moved_from=Path('old.txt')).valid

    # Valid: modified + diff
    assert DocumentDelta(Path('file.txt'), 'diff content', modified=True, diff=True).valid

def test_invalid_combinations():
    # Invalid: removed with content
    assert not DocumentDelta(Path('file.txt'), 'content', removed=True).valid

def test_equality():
    delta1 = DocumentDelta(Path('file.txt'), 'content', new=True)
    delta2 = DocumentDelta(Path('file.txt'), 'content', new=True)
    delta3 = DocumentDelta(Path('file.txt'), 'content', modified=True)

    assert delta1 == delta2
    assert delta1 != delta3
    assert delta1 != "not a delta"

def test_str():
    delta = DocumentDelta(Path('file.txt'), 'content', new=True)
    result = str(delta)
    assert 'file.txt' in result
    assert 'new' in result

    delta_complex = DocumentDelta(Path('file.txt'), 'content', modified=True, moved_from=Path('old.txt'))
    result = str(delta_complex)
    assert 'file.txt' in result
    assert 'modified' in result
    assert 'moved from old.txt' in result
