from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.deltas.documents import DocumentDelta
from llobot.knowledge.deltas.knowledge import KnowledgeDelta
from llobot.knowledge.deltas.diffs import knowledge_delta_between

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
