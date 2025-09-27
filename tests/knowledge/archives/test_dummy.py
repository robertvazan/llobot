from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.archives.dummy import dummy_knowledge_archive
from llobot.utils.text import normalize_document
from llobot.utils.time import current_time

K1 = Knowledge({
    Path('a.txt'): normalize_document('content a'),
    Path('b/c.txt'): normalize_document('content c'),
})

def test_dummy_knowledge_archive():
    archive = dummy_knowledge_archive()
    assert archive.last(Path('zone1')) == Knowledge()
    archive.add(Path('zone1'), current_time(), K1)
    assert archive.last(Path('zone1')) == Knowledge()
    time = current_time()
    archive.add(Path('zone1'), time, K1)
    archive.remove(Path('zone1'), time)
    assert archive.last(Path('zone1')) == Knowledge()
    assert archive.last(Path('some/zone')) == Knowledge()
