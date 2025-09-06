from pathlib import Path
from unittest.mock import Mock
from llobot.knowledge import Knowledge
from llobot.knowledge.archives import KnowledgeArchive, standard_knowledge_archive, coerce_knowledge_archive
from llobot.text import normalize_document
from llobot.time import current_time

K1 = Knowledge({
    Path('a.txt'): normalize_document('content a'),
    Path('b/c.txt'): normalize_document('content c'),
})

def test_standard_and_coerce(tmp_path):
    # Test standard_knowledge_archive uses tgz
    archive = standard_knowledge_archive(tmp_path)
    time = current_time()
    archive.add('zone', time, K1)
    assert archive.last('zone') == K1

    # Test coerce from path
    coerced_from_path = coerce_knowledge_archive(tmp_path)
    assert coerced_from_path.last('zone') == K1

    # Test coerce from archive instance
    coerced_from_archive = coerce_knowledge_archive(archive)
    assert coerced_from_archive is archive

def test_refresh():
    archive = KnowledgeArchive()
    k1 = Knowledge({'a': '1'})
    k2 = Knowledge({'a': '2'})

    archive.add = Mock()

    # First time, should add
    archive.last = Mock(return_value=Knowledge())
    archive.refresh('zone1', k1)
    archive.add.assert_called_once()
    archive.add.reset_mock()

    # Unchanged, should not add
    archive.last = Mock(return_value=k1)
    archive.refresh('zone1', k1)
    archive.add.assert_not_called()
    archive.add.reset_mock()

    # Changed, should add
    archive.last = Mock(return_value=k1)
    archive.refresh('zone1', k2)
    archive.add.assert_called_once()
