from llobot.formats.trees.grouped import GroupedTreeFormat
from llobot.knowledge.trees.builder import KnowledgeTreeBuilder

def test_render():
    builder = KnowledgeTreeBuilder()
    builder.add('a/b.txt')
    builder.add('a/d/e.txt')
    builder.add('c.txt')
    tree = builder.build()
    formatter = GroupedTreeFormat(title='Test Files')
    result = formatter.render(tree)
    assert '<summary>Test Files</summary>' in result
    assert 'In a:' in result
    assert '- b.txt' in result
    assert '- d/' in result
    assert '- c.txt' in result
