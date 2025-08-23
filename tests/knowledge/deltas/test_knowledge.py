from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.deltas import DocumentDelta, KnowledgeDelta

def test_init():
    deltas = [DocumentDelta(Path('file.txt'), 'content', new=True)]
    delta = KnowledgeDelta(deltas)
    expected = KnowledgeDelta([DocumentDelta(Path('file.txt'), 'content', new=True)])
    assert delta == expected

def test_bool():
    empty_delta = KnowledgeDelta()
    assert not empty_delta

    delta = KnowledgeDelta([DocumentDelta(Path('file.txt'), 'content', new=True)])
    assert bool(delta)

def test_len():
    assert len(KnowledgeDelta()) == 0

    deltas = [
        DocumentDelta(Path('file1.txt'), 'content1', new=True),
        DocumentDelta(Path('file2.txt'), 'content2', modified=True),
    ]
    assert len(KnowledgeDelta(deltas)) == 2

def test_iter():
    deltas = [
        DocumentDelta(Path('file1.txt'), 'content1', new=True),
        DocumentDelta(Path('file2.txt'), 'content2', modified=True),
    ]
    delta = KnowledgeDelta(deltas)

    assert list(delta) == deltas

def test_getitem_int():
    deltas = [
        DocumentDelta(Path('file1.txt'), 'content1', new=True),
        DocumentDelta(Path('file2.txt'), 'content2', modified=True),
    ]
    delta = KnowledgeDelta(deltas)

    assert delta[0] == deltas[0]
    assert delta[1] == deltas[1]

def test_getitem_slice():
    deltas = [
        DocumentDelta(Path('file1.txt'), 'content1', new=True),
        DocumentDelta(Path('file2.txt'), 'content2', modified=True),
        DocumentDelta(Path('file3.txt'), 'content3', removed=True),
    ]
    delta = KnowledgeDelta(deltas)

    sliced = delta[1:3]
    expected = KnowledgeDelta(deltas[1:3])
    assert sliced == expected

def test_equality():
    deltas1 = [DocumentDelta(Path('file1.txt'), 'content1', new=True)]
    deltas2 = [DocumentDelta(Path('file1.txt'), 'content1', new=True)]
    deltas3 = [DocumentDelta(Path('file2.txt'), 'content2', modified=True)]

    delta1 = KnowledgeDelta(deltas1)
    delta2 = KnowledgeDelta(deltas2)
    delta3 = KnowledgeDelta(deltas3)

    assert delta1 == delta2
    assert delta1 != delta3
    assert delta1 != "not a delta"

def test_str():
    deltas = [
        DocumentDelta(Path('file1.txt'), 'content1', new=True),
        DocumentDelta(Path('file2.txt'), 'content2', modified=True),
    ]
    delta = KnowledgeDelta(deltas)

    result = str(delta)
    assert result.startswith('[')
    assert result.endswith(']')
    assert 'file1.txt' in result
    assert 'file2.txt' in result

def test_add():
    delta1 = KnowledgeDelta([DocumentDelta(Path('file1.txt'), 'content1', new=True)])
    delta2 = KnowledgeDelta([DocumentDelta(Path('file2.txt'), 'content2', modified=True)])

    combined = delta1 + delta2
    expected = KnowledgeDelta([
        DocumentDelta(Path('file1.txt'), 'content1', new=True),
        DocumentDelta(Path('file2.txt'), 'content2', modified=True)
    ])
    assert combined == expected

def test_touched():
    deltas = [
        DocumentDelta(Path('new.txt'), 'content', new=True),
        DocumentDelta(Path('modified.txt'), 'content', modified=True),
        DocumentDelta(Path('removed.txt'), None, removed=True),
        DocumentDelta(Path('moved.txt'), None, moved_from=Path('old.txt')),
    ]
    delta = KnowledgeDelta(deltas)

    touched = delta.touched
    expected_paths = {
        Path('new.txt'), Path('modified.txt'), Path('removed.txt'),
        Path('moved.txt'), Path('old.txt')
    }
    assert set(touched) == expected_paths

def test_present():
    deltas = [
        DocumentDelta(Path('new.txt'), 'content', new=True),
        DocumentDelta(Path('modified.txt'), 'content', modified=True),
        DocumentDelta(Path('removed.txt'), None, removed=True),
        DocumentDelta(Path('moved.txt'), None, moved_from=Path('old.txt')),
    ]
    delta = KnowledgeDelta(deltas)

    present = delta.present
    expected_paths = {Path('new.txt'), Path('modified.txt'), Path('moved.txt')}
    assert set(present) == expected_paths

def test_removed():
    deltas = [
        DocumentDelta(Path('new.txt'), 'content', new=True),
        DocumentDelta(Path('modified.txt'), 'content', modified=True),
        DocumentDelta(Path('removed.txt'), None, removed=True),
        DocumentDelta(Path('moved.txt'), None, moved_from=Path('old.txt')),
    ]
    delta = KnowledgeDelta(deltas)

    removed = delta.removed
    expected_paths = {Path('removed.txt'), Path('old.txt')}
    assert set(removed) == expected_paths

def test_full():
    deltas = [
        DocumentDelta(Path('new.txt'), 'new content', new=True),
        DocumentDelta(Path('modified.txt'), 'modified content', modified=True),
        DocumentDelta(Path('removed.txt'), None, removed=True),
        DocumentDelta(Path('moved.txt'), None, moved_from=Path('old.txt')),
        DocumentDelta(Path('diff.txt'), 'diff content', modified=True, diff=True),
    ]
    delta = KnowledgeDelta(deltas)

    full = delta.full
    expected = Knowledge({
        Path('new.txt'): 'new content',
        Path('modified.txt'): 'modified content',
    })
    assert full == expected

def test_moves():
    deltas = [
        DocumentDelta(Path('moved1.txt'), None, moved_from=Path('old1.txt')),
        DocumentDelta(Path('moved2.txt'), 'content', modified=True, moved_from=Path('old2.txt')),
    ]
    delta = KnowledgeDelta(deltas)

    moves = delta.moves
    expected = {
        Path('moved1.txt'): Path('old1.txt'),
        Path('moved2.txt'): Path('old2.txt')
    }
    assert moves == expected

def test_moves_chained():
    # Test case where moves are chained (A -> B -> C)
    # Process in the order that creates the chain correctly
    deltas = [
        DocumentDelta(Path('b.txt'), None, moved_from=Path('a.txt')),
        DocumentDelta(Path('c.txt'), None, moved_from=Path('b.txt')),
    ]
    delta = KnowledgeDelta(deltas)

    moves = delta.moves
    expected = {
        Path('b.txt'): Path('a.txt'),
        Path('c.txt'): Path('a.txt')  # Should trace back to ultimate source
    }
    assert moves == expected
