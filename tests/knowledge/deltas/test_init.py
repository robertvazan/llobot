from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.deltas import fresh, between, diff_compress, DocumentDelta, KnowledgeDelta

def test_fresh():
    knowledge = Knowledge({
        Path('file1.txt'): 'content1',
        Path('file2.txt'): 'content2',
    })

    delta = fresh(knowledge)

    expected = KnowledgeDelta([
        DocumentDelta(Path('file1.txt'), 'content1'),
        DocumentDelta(Path('file2.txt'), 'content2'),
    ])
    assert delta == expected

def test_between_with_addition():
    before = Knowledge({Path('existing.txt'): 'content'})
    after = Knowledge({
        Path('existing.txt'): 'content',
        Path('new_file.txt'): 'new content',
    })

    delta = between(before, after)

    expected = KnowledgeDelta([
        DocumentDelta(Path('new_file.txt'), 'new content', new=True)
    ])
    assert delta == expected

def test_between_with_modification():
    before = Knowledge({Path('file.txt'): 'old content'})
    after = Knowledge({Path('file.txt'): 'new content'})

    delta = between(before, after)

    expected = KnowledgeDelta([
        DocumentDelta(Path('file.txt'), 'new content', modified=True)
    ])
    assert delta == expected

def test_between_with_removal():
    before = Knowledge({Path('file.txt'): 'content'})
    after = Knowledge({})

    delta = between(before, after)

    expected = KnowledgeDelta([
        DocumentDelta(Path('file.txt'), None, removed=True)
    ])
    assert delta == expected

def test_between_with_move_hints():
    before = Knowledge({Path('old.txt'): 'content'})
    after = Knowledge({Path('new.txt'): 'content'})
    move_hints = {Path('new.txt'): Path('old.txt')}

    delta = between(before, after, move_hints=move_hints)

    expected = KnowledgeDelta([
        DocumentDelta(Path('new.txt'), None, moved_from=Path('old.txt'))
    ])
    assert delta == expected

def test_diff_compress():
    # Use much longer content to ensure compression happens
    long_content = '\n'.join([f'line {i}' for i in range(20)])
    modified_content = '\n'.join([f'line {i}' if i != 10 else 'changed line 10' for i in range(20)])

    before = Knowledge({Path('file.txt'): long_content})

    # Create delta with small change (only one line changed out of 20)
    delta = KnowledgeDelta([
        DocumentDelta(Path('file.txt'), modified_content, modified=True)
    ])

    compressed = diff_compress(before, delta, threshold=0.9)

    # Should be compressed to diff format
    compressed_delta = next(iter(compressed))
    assert compressed_delta.diff
    assert '@@' in compressed_delta.content  # Unified diff format

def test_diff_compress_no_change():
    before = Knowledge({Path('file.txt'): 'content'})

    # Create delta with no actual change
    delta = KnowledgeDelta([
        DocumentDelta(Path('file.txt'), 'content', modified=True)
    ])

    compressed = diff_compress(before, delta)

    # Should be empty since there's no actual change
    assert compressed == KnowledgeDelta()

def test_diff_compress_threshold():
    before = Knowledge({Path('file.txt'): 'short'})

    # Create delta with large change that won't compress well
    delta = KnowledgeDelta([
        DocumentDelta(Path('file.txt'), 'completely different and much longer content', modified=True)
    ])

    compressed = diff_compress(before, delta, threshold=0.1)  # Very low threshold

    # Should not be compressed due to threshold
    expected = KnowledgeDelta([
        DocumentDelta(Path('file.txt'), 'completely different and much longer content', modified=True)
    ])
    assert compressed == expected
