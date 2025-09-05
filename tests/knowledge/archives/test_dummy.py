from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.archives.dummy import dummy_knowledge_archive
from llobot.text import normalize_document
from llobot.time import current_time

K1 = Knowledge({
    Path('a.txt'): normalize_document('content a'),
    Path('b/c.txt'): normalize_document('content c'),
})

def test_dummy_knowledge_archive():
    archive = dummy_knowledge_archive()
    assert archive.last('zone1') == Knowledge()
    archive.add('zone1', current_time(), K1)
    assert archive.last('zone1') == Knowledge()
    time = current_time()
    archive.add('zone1', time, K1)
    archive.remove('zone1', time)
    assert archive.last('zone1') == Knowledge()
