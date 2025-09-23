from pathlib import Path
from llobot.formats.deltas.knowledge import standard_knowledge_delta_format
from llobot.knowledge.deltas.documents import DocumentDelta
from llobot.knowledge.deltas.knowledge import KnowledgeDelta

def test_render():
    formatter = standard_knowledge_delta_format()
    delta = KnowledgeDelta([
        DocumentDelta(Path('file1.py'), 'content1'),
        DocumentDelta(Path('file2.py'), None, removed=True),
        DocumentDelta(Path('file3.py'), None, moved_from=Path('old3.py'))
    ])
    result = formatter.render(delta)
    assert 'File: file1.py' in result
    assert 'Removed: `file2.py`' in result
    assert 'Moved: `old3.py` => `file3.py`' in result
