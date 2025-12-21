from pathlib import PurePosixPath
from llobot.knowledge import Knowledge
from llobot.knowledge.indexes import KnowledgeIndex
from llobot.knowledge.ranking import KnowledgeRanking
from llobot.knowledge.resolver import KnowledgeResolver, cached_knowledge_resolver

def test_resolver_creation():
    index = KnowledgeIndex([
        PurePosixPath('src/main.py'),
        PurePosixPath('src/utils/helper.py'),
        PurePosixPath('test/test_main.py'),
        PurePosixPath('README.md'),
    ])
    resolver = KnowledgeResolver(index)

    # Test names mapping
    assert PurePosixPath('src/main.py') in resolver._names['main.py']
    assert PurePosixPath('test/test_main.py') in resolver._names['test_main.py']
    assert PurePosixPath('README.md') in resolver._names['README.md']

    # Test tails mapping
    assert PurePosixPath('src/utils/helper.py') in resolver._tails[PurePosixPath('utils/helper.py')]

def test_create_resolver_from_knowledge():
    knowledge = Knowledge({PurePosixPath('src/main.py'): 'content', PurePosixPath('README.md'): 'content'})
    resolver = cached_knowledge_resolver(knowledge)
    assert isinstance(resolver, KnowledgeResolver)

def test_create_resolver_from_index():
    index = KnowledgeIndex([PurePosixPath('src/main.py'), PurePosixPath('README.md')])
    resolver = cached_knowledge_resolver(index)
    assert isinstance(resolver, KnowledgeResolver)

def test_create_resolver_from_ranking():
    ranking = KnowledgeRanking([PurePosixPath('src/main.py'), PurePosixPath('README.md')])
    resolver = cached_knowledge_resolver(ranking)
    assert isinstance(resolver, KnowledgeResolver)

def test_resolve_all():
    index = KnowledgeIndex([
        PurePosixPath('src/main.py'),
        PurePosixPath('src/utils/helper.py'),
        PurePosixPath('test/main.py'),
    ])
    resolver = KnowledgeResolver(index)
    assert resolver.resolve_all(PurePosixPath('main.py')) == KnowledgeIndex(['src/main.py', 'test/main.py'])
    assert resolver.resolve_all(PurePosixPath('utils/helper.py')) == KnowledgeIndex(['src/utils/helper.py'])
    assert resolver.resolve_all(PurePosixPath('nonexistent.py')) == KnowledgeIndex()
    assert resolver.resolve_all(PurePosixPath('main.py'), PurePosixPath('helper.py')) == KnowledgeIndex(['src/main.py', 'test/main.py', 'src/utils/helper.py'])

def test_resolve():
    index = KnowledgeIndex([
        PurePosixPath('src/main.py'),
        PurePosixPath('src/utils/helper.py'),
        PurePosixPath('test/main.py'),
    ])
    resolver = KnowledgeResolver(index)
    assert resolver.resolve(PurePosixPath('main.py')) is None
    assert resolver.resolve(PurePosixPath('utils/helper.py')) == PurePosixPath('src/utils/helper.py')
    assert resolver.resolve(PurePosixPath('helper.py')) == PurePosixPath('src/utils/helper.py')
    assert resolver.resolve(PurePosixPath('nonexistent.py')) is None

def test_resolve_all_near():
    index = KnowledgeIndex([
        PurePosixPath('src/main.py'),
        PurePosixPath('src/utils/helper.py'),
        PurePosixPath('test/main.py'),
        PurePosixPath('test/utils/helper.py'),
    ])
    resolver = KnowledgeResolver(index)
    # Disambiguation
    assert resolver.resolve_all_near(PurePosixPath('src/some_other_file.py'), PurePosixPath('main.py')) == KnowledgeIndex(['src/main.py'])
    assert resolver.resolve_all_near(PurePosixPath('test/some_other_file.py'), PurePosixPath('main.py')) == KnowledgeIndex(['test/main.py'])
    # Tie
    assert resolver.resolve_all_near(PurePosixPath('root.py'), PurePosixPath('main.py')) == KnowledgeIndex(['src/main.py', 'test/main.py'])
    # Single result
    assert resolver.resolve_all_near(PurePosixPath('src'), PurePosixPath('utils/helper.py')) == KnowledgeIndex(['src/utils/helper.py'])

def test_resolve_near():
    index = KnowledgeIndex([
        PurePosixPath('src/main.py'),
        PurePosixPath('src/utils/helper.py'),
        PurePosixPath('test/main.py'),
    ])
    resolver = KnowledgeResolver(index)
    # Disambiguation
    assert resolver.resolve_near(PurePosixPath('src/other.py'), PurePosixPath('main.py')) == PurePosixPath('src/main.py')
    assert resolver.resolve_near(PurePosixPath('test/other.py'), PurePosixPath('main.py')) == PurePosixPath('test/main.py')
    # No match
    assert resolver.resolve_near(PurePosixPath('src/other.py'), PurePosixPath('nonexistent.py')) is None
    # Tie
    assert resolver.resolve_near(PurePosixPath('root.py'), PurePosixPath('main.py')) is None
