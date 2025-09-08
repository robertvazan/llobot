from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.deltas.documents import DocumentDelta
from llobot.knowledge.deltas.knowledge import KnowledgeDelta
from llobot.knowledge.deltas.compression import compress_knowledge_delta

def test_compress():
    # Use much longer content to ensure compression happens
    long_content = '\n'.join([f'line {i}' for i in range(20)])
    modified_content = '\n'.join([f'line {i}' if i != 10 else 'changed line 10' for i in range(20)])

    before = Knowledge({Path('file.txt'): long_content})

    # Create delta with small change (only one line changed out of 20)
    delta = KnowledgeDelta([
        DocumentDelta(Path('file.txt'), modified_content)
    ])

    compressed = compress_knowledge_delta(before, delta, threshold=0.9)

    # Should be compressed to diff format
    compressed_delta = next(iter(compressed))
    assert compressed_delta.diff
    assert '@@' in compressed_delta.content  # Unified diff format

def test_compress_no_change():
    before = Knowledge({Path('file.txt'): 'content'})

    # Create delta with no actual change
    delta = KnowledgeDelta([
        DocumentDelta(Path('file.txt'), 'content')
    ])

    compressed = compress_knowledge_delta(before, delta)

    # Should be empty since there's no actual change
    assert compressed == KnowledgeDelta()

def test_compress_threshold():
    before = Knowledge({Path('file.txt'): 'short'})

    # Create delta with large change that won't compress well
    delta = KnowledgeDelta([
        DocumentDelta(Path('file.txt'), 'completely different and much longer content')
    ])

    compressed = compress_knowledge_delta(before, delta, threshold=0.1)  # Very low threshold

    # Should not be compressed due to threshold
    expected = KnowledgeDelta([
        DocumentDelta(Path('file.txt'), 'completely different and much longer content')
    ])
    assert compressed == expected
