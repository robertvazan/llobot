from llobot.formats.trees.flat import FlatTreeFormat
from llobot.knowledge.trees.builder import KnowledgeTreeBuilder

def test_render():
    builder = KnowledgeTreeBuilder()
    builder.add('a/b.txt')
    builder.add('c.txt')
    tree = builder.build()
    formatter = FlatTreeFormat(title='Test Files')
    result = formatter.render(tree)
    assert '<summary>Test Files</summary>' in result
    assert 'a/b.txt' in result
    assert 'c.txt' in result
    assert result.count('\n') > 2
