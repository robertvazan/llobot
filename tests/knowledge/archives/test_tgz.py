from pathlib import Path
from datetime import timedelta
from llobot.knowledge import Knowledge
from llobot.knowledge.archives.tgz import (
    TgzKnowledgeArchive,
    serialize_knowledge_tgz,
    deserialize_knowledge_tgz,
    save_knowledge_tgz,
    load_knowledge_tgz,
)
from llobot.utils.text import normalize_document
from llobot.utils.time import current_time

K1 = Knowledge({
    Path('a.txt'): normalize_document('content a'),
    Path('b/c.txt'): normalize_document('content c'),
})
K2 = Knowledge({
    Path('a.txt'): normalize_document('new content a'),
    Path('d.txt'): normalize_document('content d'),
})

def test_tgz_serialization():
    serialized = serialize_knowledge_tgz(K1)
    deserialized = deserialize_knowledge_tgz(serialized)
    assert deserialized == K1

def test_tgz_save_load(tmp_path):
    path = tmp_path / 'test.tar.gz'
    save_knowledge_tgz(path, K1)
    loaded = load_knowledge_tgz(path)
    assert loaded == K1

def test_tgz_knowledge_archive(tmp_path):
    archive = TgzKnowledgeArchive(tmp_path)

    time1 = current_time()
    archive.add(Path('zone1/sub'), time1, K1)

    # Make sure we get a different timestamp without slowing down the test.
    time2 = time1 + timedelta(seconds=1)
    archive.add(Path('zone1/sub'), time2, K2)

    assert archive.last(Path('zone1/sub')) == K2
    assert archive.last(Path('zone1/sub'), time2) == K2
    assert archive.last(Path('zone1/sub'), time1) == K1
    assert archive.last(Path('zone2')) == Knowledge()

    archive.remove(Path('zone1/sub'), time2)
    assert archive.last(Path('zone1/sub')) == K1

    archive.remove(Path('zone1/sub'), time1)
    assert archive.last(Path('zone1/sub')) == Knowledge()
