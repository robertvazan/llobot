from llobot.formats.indexes.flat import FlatIndexFormat
from llobot.knowledge.indexes import KnowledgeIndex

def test_render():
    index = KnowledgeIndex(['c.txt', 'a/b.txt'])
    formatter = FlatIndexFormat()
    result = formatter.render(index)
    # standard_ranker sorts lexicographically, so a/b.txt comes first.
    assert result == 'a/b.txt\nc.txt'
