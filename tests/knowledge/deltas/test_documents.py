import pytest
from pathlib import Path
from llobot.knowledge.deltas.documents import DocumentDelta

def test_init():
    delta = DocumentDelta(Path('file.txt'), 'content')

    assert delta.path == Path('file.txt')
    assert delta.content == 'content'
    assert not delta.removed
    assert not delta.diff
    assert not delta.moved
    assert delta.moved_from is None

def test_path():
    delta = DocumentDelta(Path('test/file.txt'), 'content')
    assert delta.path == Path('test/file.txt')

def test_removed():
    delta_removed = DocumentDelta(Path('file.txt'), None, removed=True)
    assert delta_removed.removed

    delta_not_removed = DocumentDelta(Path('file.txt'), 'content')
    assert not delta_not_removed.removed

def test_diff():
    delta_diff = DocumentDelta(Path('file.txt'), 'diff content', diff=True)
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
    # Valid: regular file with content
    DocumentDelta(Path('file.txt'), 'content')

    # Valid: diff file
    DocumentDelta(Path('file.txt'), 'diff content', diff=True)

    # Valid: removed file (no content)
    DocumentDelta(Path('file.txt'), None, removed=True)

    # Valid: moved file (no content)
    DocumentDelta(Path('new.txt'), None, moved_from=Path('old.txt'))

def test_invalid_combinations():
    # Invalid: removed with content
    with pytest.raises(ValueError, match="Removed files cannot have content"):
        DocumentDelta(Path('file.txt'), 'content', removed=True)

    # Invalid: moved with content
    with pytest.raises(ValueError, match="Moved files cannot have content"):
        DocumentDelta(Path('new.txt'), 'content', moved_from=Path('old.txt'))

    # Invalid: regular file without content
    with pytest.raises(ValueError, match="Regular files must have content"):
        DocumentDelta(Path('file.txt'), None)

    # Invalid: diff without content
    with pytest.raises(ValueError, match="Diff files must have content"):
        DocumentDelta(Path('file.txt'), None, diff=True)

    # Invalid: removed with diff flag
    with pytest.raises(ValueError, match="Removed files cannot have other flags"):
        DocumentDelta(Path('file.txt'), None, removed=True, diff=True)

    # Invalid: moved with diff flag
    with pytest.raises(ValueError, match="Moved files cannot have diff flag"):
        DocumentDelta(Path('file.txt'), None, moved_from=Path('old.txt'), diff=True)

def test_equality():
    delta1 = DocumentDelta(Path('file.txt'), 'content')
    delta2 = DocumentDelta(Path('file.txt'), 'content')
    delta3 = DocumentDelta(Path('file.txt'), 'other content')

    assert delta1 == delta2
    assert delta1 != delta3
    assert delta1 != "not a delta"

def test_str():
    delta = DocumentDelta(Path('file.txt'), 'content')
    result = str(delta)
    assert result == 'file.txt'

    delta_with_flags = DocumentDelta(Path('file.txt'), 'content', diff=True)
    result = str(delta_with_flags)
    assert 'file.txt' in result
    assert 'diff' in result

    delta_complex = DocumentDelta(Path('new.txt'), None, moved_from=Path('old.txt'))
    result = str(delta_complex)
    assert 'new.txt' in result
    assert 'moved from old.txt' in result
