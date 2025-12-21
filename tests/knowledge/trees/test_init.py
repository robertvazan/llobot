from pathlib import PurePosixPath
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.ranking import KnowledgeRanking
from llobot.knowledge.trees import KnowledgeTree, standard_tree, coerce_tree

def test_knowledge_tree_value_semantics():
    t1 = KnowledgeTree('a', files=['b'])
    t2 = KnowledgeTree('a', files=['b'])
    t3 = KnowledgeTree('a', files=['c'])
    assert t1 == t2
    assert t1 != t3
    assert hash(t1) == hash(t2)
    assert hash(t1) != hash(t3)
    assert repr(t1) == f"KnowledgeTree(base={repr(PurePosixPath('a'))}, files=('b',), subtrees=())"

def test_coerce_tree():
    knowledge = Knowledge({PurePosixPath('b.txt'): '', PurePosixPath('a/c.txt'): ''})
    ranking = KnowledgeRanking([PurePosixPath('b.txt'), PurePosixPath('a/c.txt')])
    index = KnowledgeIndex([PurePosixPath('b.txt'), PurePosixPath('a/c.txt')])
    tree = KnowledgeTree(files=['b.txt'], subtrees=[KnowledgeTree('a', files=['c.txt'])])

    assert coerce_tree(tree) is tree

    coerced_from_ranking = coerce_tree(ranking)
    assert coerced_from_ranking.files == ['b.txt']
    assert coerced_from_ranking.subtrees[0].base == PurePosixPath('a')
    assert coerced_from_ranking.subtrees[0].files == ['c.txt']

    # coerce_ranking on index is lexicographical: a/c.txt, b.txt
    # ranked_tree reorders them to b.txt, a/c.txt
    coerced_from_index = coerce_tree(index)
    assert coerced_from_index.all_paths == [PurePosixPath('b.txt'), PurePosixPath('a/c.txt')]

    coerced_from_knowledge = coerce_tree(knowledge)
    assert coerced_from_knowledge.all_paths == [PurePosixPath('b.txt'), PurePosixPath('a/c.txt')]

def test_standard_tree():
    knowledge = Knowledge({PurePosixPath('a/z.txt'): '', PurePosixPath('a/README.md'): ''})
    tree = standard_tree(knowledge)
    # standard_tree -> overviews_first_tree -> rank_overviews_first -> ranked_tree
    # coerce_ranking gives lexicographical: a/README.md, a/z.txt
    # rank_overviews_first on this with overviews_subset (matching README.md)
    # results in the same order. Then ranked_tree.
    assert tree.all_paths == [PurePosixPath('a/README.md'), PurePosixPath('a/z.txt')]
