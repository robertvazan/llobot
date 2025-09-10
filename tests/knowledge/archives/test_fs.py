from pathlib import Path
from llobot.knowledge import Knowledge
from llobot.knowledge.archives.fs import save_knowledge_directory, load_knowledge_directory
from llobot.utils.text import normalize_document

K1 = Knowledge({
    Path('a.txt'): normalize_document('content a'),
    Path('b/c.txt'): normalize_document('content c'),
})

def test_fs_knowledge_directory(tmp_path):
    save_knowledge_directory(tmp_path, K1)
    assert (tmp_path / 'a.txt').read_text() == 'content a\n'
    assert (tmp_path / 'b' / 'c.txt').read_text() == 'content c\n'

    loaded = load_knowledge_directory(tmp_path)
    assert loaded == K1
