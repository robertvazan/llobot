from llobot.formats.indexes.grouped import GroupedIndexFormat
from llobot.knowledge import Knowledge
from llobot.utils.text import normalize_document

def test_render():
    knowledge = Knowledge({'c.txt': '', 'a/b.txt': '', 'a/d/e.txt': ''})
    formatter = GroupedIndexFormat()
    result = formatter.render(knowledge)
    # The default ranker sorts paths lexicographically. The grouped format
    # then lists files and directories for each tree level.
    expected = """
- c.txt
- a/

In a:
- b.txt
- d/

In a/d:
- e.txt
    """
    assert normalize_document(result) == normalize_document(expected)
