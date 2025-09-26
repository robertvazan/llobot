from llobot.formats.indexes.flat import FlatIndexFormat
from llobot.knowledge import Knowledge

def test_render():
    knowledge = Knowledge({'c.txt': '', 'a/b.txt': ''})
    formatter = FlatIndexFormat()
    result = formatter.render(knowledge)
    # standard_ranker does a pre-order traversal of a tree built from
    # lexicographically sorted paths. 'c.txt' at root comes before 'a/b.txt'.
    assert result == 'c.txt\na/b.txt'
