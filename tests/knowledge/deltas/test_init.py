from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.deltas import fresh_knowledge_delta, knowledge_delta_between, diff_compress_knowledge, DocumentDelta, KnowledgeDelta

def test_fresh():
    knowledge = Knowledge({
        Path('file1.txt'): 'content1',
        Path('file2.txt'): 'content2',
    })

    delta = fresh_knowledge_delta(knowledge)

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

    delta = knowledge_delta_between(before, after)

    expected = KnowledgeDelta([
        DocumentDelta(Path('new_file.txt'), 'new content')
    ])
    assert delta == expected

def test_between_with_modification():
    before = Knowledge({Path('file.txt'): 'old content'})
    after = Knowledge({Path('file.txt'): 'new content'})

    delta = knowledge_delta_between(before, after)

    expected = KnowledgeDelta([
        DocumentDelta(Path('file.txt'), 'new content')
    ])
    assert delta == expected

def test_between_with_removal():
    before = Knowledge({Path('file.txt'): 'content'})
    after = Knowledge({})

    delta = knowledge_delta_between(before, after)

    expected = KnowledgeDelta([
        DocumentDelta(Path('file.txt'), None, removed=True)
    ])
    assert delta == expected

def test_between_with_move():
    before = Knowledge({Path('old.txt'): 'content'})
    after = Knowledge({Path('new.txt'): 'content'})

    delta = knowledge_delta_between(before, after)

    expected = KnowledgeDelta([
        DocumentDelta(Path('old.txt'), None, removed=True),
        DocumentDelta(Path('new.txt'), 'content'),
    ])
    assert delta == expected

def test_diff_compress():
    # Use much longer content to ensure compression happens
    long_content = '\n'.join([f'line {i}' for i in range(20)])
    modified_content = '\n'.join([f'line {i}' if i != 10 else 'changed line 10' for i in range(20)])

    before = Knowledge({Path('file.txt'): long_content})

    # Create delta with small change (only one line changed out of 20)
    delta = KnowledgeDelta([
        DocumentDelta(Path('file.txt'), modified_content)
    ])

    compressed = diff_compress_knowledge(before, delta, threshold=0.9)

    # Should be compressed to diff format
    compressed_delta = next(iter(compressed))
    assert compressed_delta.diff
    assert '@@' in compressed_delta.content  # Unified diff format

def test_diff_compress_no_change():
    before = Knowledge({Path('file.txt'): 'content'})

    # Create delta with no actual change
    delta = KnowledgeDelta([
        DocumentDelta(Path('file.txt'), 'content')
    ])

    compressed = diff_compress_knowledge(before, delta)

    # Should be empty since there's no actual change
    assert compressed == KnowledgeDelta()

def test_diff_compress_threshold():
    before = Knowledge({Path('file.txt'): 'short'})

    # Create delta with large change that won't compress well
    delta = KnowledgeDelta([
        DocumentDelta(Path('file.txt'), 'completely different and much longer content')
    ])

    compressed = diff_compress_knowledge(before, delta, threshold=0.1)  # Very low threshold

    # Should not be compressed due to threshold
    expected = KnowledgeDelta([
        DocumentDelta(Path('file.txt'), 'completely different and much longer content')
    ])
    assert compressed == expected
