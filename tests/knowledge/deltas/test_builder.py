from pathlib import Path
from llobot.knowledge.deltas.documents import DocumentDelta
from llobot.knowledge.deltas.knowledge import KnowledgeDelta
from llobot.knowledge.deltas.builder import KnowledgeDeltaBuilder

def test_init():
    builder = KnowledgeDeltaBuilder()
    result = builder.build()
    assert result == KnowledgeDelta()

def test_add_document_delta():
    builder = KnowledgeDeltaBuilder()
    delta = DocumentDelta(Path('file.txt'), 'content')

    builder.add(delta)
    result = builder.build()

    expected = KnowledgeDelta([delta])
    assert result == expected

def test_add_knowledge_delta():
    builder = KnowledgeDeltaBuilder()
    deltas = [
        DocumentDelta(Path('file1.txt'), 'content1'),
        DocumentDelta(Path('file2.txt'), 'content2'),
    ]
    knowledge_delta = KnowledgeDelta(deltas)

    builder.add(knowledge_delta)
    result = builder.build()

    assert result == knowledge_delta

def test_add_mixed_types():
    builder = KnowledgeDeltaBuilder()

    # Add individual document delta
    doc_delta = DocumentDelta(Path('file1.txt'), 'content1')
    builder.add(doc_delta)

    # Add knowledge delta with multiple documents
    knowledge_delta = KnowledgeDelta([
        DocumentDelta(Path('file2.txt'), 'content2'),
        DocumentDelta(Path('file3.txt'), None, removed=True),
    ])
    builder.add(knowledge_delta)

    result = builder.build()
    expected = KnowledgeDelta([
        doc_delta,
        DocumentDelta(Path('file2.txt'), 'content2'),
        DocumentDelta(Path('file3.txt'), None, removed=True),
    ])
    assert result == expected

def test_add_invalid_type():
    builder = KnowledgeDeltaBuilder()

    try:
        builder.add("invalid")
        assert False, "Should have raised TypeError"
    except TypeError as e:
        assert "Unsupported type" in str(e)

def test_build():
    builder = KnowledgeDeltaBuilder()
    delta1 = DocumentDelta(Path('file1.txt'), 'content1')
    delta2 = DocumentDelta(Path('file2.txt'), 'content2')

    builder.add(delta1)
    builder.add(delta2)

    result = builder.build()
    expected = KnowledgeDelta([delta1, delta2])
    assert result == expected

def test_build_empty():
    builder = KnowledgeDeltaBuilder()
    result = builder.build()

    assert result == KnowledgeDelta()
    assert not result
