from llobot.formats.trees import standard_tree_format
from llobot.formats.trees.grouped import GroupedTreeFormat
from llobot.knowledge.trees.builder import KnowledgeTreeBuilder

def test_standard_tree_format():
    formatter = standard_tree_format()
    assert isinstance(formatter, GroupedTreeFormat)

def test_render_chat():
    builder = KnowledgeTreeBuilder()
    builder.add('a.txt')
    tree = builder.build()
    formatter = standard_tree_format()
    chat = formatter.render_chat(tree)
    assert len(chat) == 2
    assert 'a.txt' in chat.monolithic()
